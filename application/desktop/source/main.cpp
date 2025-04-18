#include "imgui.h"
#include "imgui_impl_win32.h"
#include "imgui_impl_dx12.h"
#include <d3d12.h>
#include <dxgi1_4.h>
#include <tchar.h>
#include <windows.h>
#include <string>
#include <vector>
#include <sstream>
#include <algorithm>
#include <map>

struct FrameContext {
    ID3D12CommandAllocator* CommandAllocator;
    UINT64 FenceValue;
};


static int const NUM_FRAMES_IN_FLIGHT = 3;
static FrameContext g_frameContext[NUM_FRAMES_IN_FLIGHT] = {};
static UINT g_frameIndex = 0;
static ID3D12Device* g_pd3dDevice = NULL;
static ID3D12DescriptorHeap* g_pd3dRtvDescHeap = NULL;
static ID3D12DescriptorHeap* g_pd3dSrvDescHeap = NULL;
static ID3D12CommandQueue* g_pd3dCommandQueue = NULL;
static ID3D12GraphicsCommandList* g_pd3dCommandList = NULL;
static ID3D12Fence* g_fence = NULL;
static HANDLE g_fenceEvent = NULL;
static UINT64 g_fenceLastSignaledValue = 0;
static IDXGISwapChain3* g_pSwapChain = NULL;
static HANDLE g_hSwapChainWaitableObject = NULL;
static ID3D12Resource* g_mainRenderTargetResource[NUM_FRAMES_IN_FLIGHT] = {};
static D3D12_CPU_DESCRIPTOR_HANDLE g_mainRenderTargetDescriptor[NUM_FRAMES_IN_FLIGHT] = {};

struct Cell {
    bool isWall;
    bool isStart;
    bool isEnd;

    Cell() : isWall(false), isStart(false), isEnd(false) {}
};

struct CellCoord {
    int x, y;

    CellCoord() : x(0), y(0) {}
    CellCoord(int _x, int _y) : x(_x), y(_y) {}

    bool operator==(const CellCoord& other) const {
        return x == other.x && y == other.y;
    }

    bool operator<(const CellCoord& other) const {
        return (x < other.x) || (x == other.x && y < other.y);
    }
};

enum CommandType {
    CMD_NONE,
    CMD_MOVE_LEFT,
    CMD_MOVE_RIGHT,
    CMD_MOVE_UP,
    CMD_MOVE_DOWN,
    CMD_JUMP_TO,
    CMD_WAIT
};

struct GridCommand {
    CommandType type;
    int x;
    int y;
    int steps;

    GridCommand() : type(CMD_NONE), x(0), y(0), steps(1) {}
    GridCommand(CommandType t, int s = 1) : type(t), x(0), y(0), steps(s) {}
    GridCommand(CommandType t, int _x, int _y) : type(t), x(_x), y(_y), steps(1) {}
};


const int DEFAULT_GRID_SIZE = 10;
const float CELL_PADDING = 2.0f;
const float ANIMATION_SPEED = 5.0f;

bool CreateDeviceD3D(HWND hWnd);
void CleanupDeviceD3D();
void CreateRenderTarget();
void CleanupRenderTarget();
void WaitForLastSubmittedFrame();
FrameContext* WaitForNextFrameResources();
LRESULT WINAPI WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);
std::vector<GridCommand> ParseGridCommands(const char* commandText);
void ExecuteGridCommand(GridCommand& cmd, CellCoord& position, const std::vector<std::vector<Cell>>& grid, bool& completed);
void InitializeDefaultGrid(std::vector<std::vector<Cell>>& grid, int size);

extern IMGUI_IMPL_API LRESULT ImGui_ImplWin32_WndProcHandler(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);

int main(int, char**)
{
    WNDCLASSEXW wc = { sizeof(WNDCLASSEXW), CS_CLASSDC, WndProc, 0L, 0L, GetModuleHandle(NULL), NULL, NULL, NULL, NULL, L"ImGui Grid", NULL };
    ::RegisterClassExW(&wc);

    HWND hwnd = ::CreateWindowW(wc.lpszClassName, L"ImGui Grid Demo", WS_OVERLAPPEDWINDOW, 100, 100, 1024, 768, NULL, NULL, wc.hInstance, NULL);

    if (!CreateDeviceD3D(hwnd))
    {
        CleanupDeviceD3D();
        ::UnregisterClassW(wc.lpszClassName, wc.hInstance);
        return 1;
    }

    ::ShowWindow(hwnd, SW_SHOWDEFAULT);
    ::UpdateWindow(hwnd);

    IMGUI_CHECKVERSION();
    ImGui::CreateContext();
    ImGuiIO& io = ImGui::GetIO(); (void)io;
    io.ConfigFlags |= ImGuiConfigFlags_NavEnableKeyboard;

    ImGui::StyleColorsDark();

    ImGui_ImplWin32_Init(hwnd);
    ImGui_ImplDX12_Init(g_pd3dDevice, NUM_FRAMES_IN_FLIGHT,
        DXGI_FORMAT_R8G8B8A8_UNORM, g_pd3dSrvDescHeap,
        g_pd3dSrvDescHeap->GetCPUDescriptorHandleForHeapStart(),
        g_pd3dSrvDescHeap->GetGPUDescriptorHandleForHeapStart());

    std::vector<std::vector<Cell>> grid;
    int gridSize = DEFAULT_GRID_SIZE;
    InitializeDefaultGrid(grid, gridSize);

    float cellSize = 40.0f;
    // позиция
    CellCoord squarePos(0, 0);
    CellCoord targetPos = squarePos;
    float animX = 0.0f;
    float animY = 0.0f;
    bool isAnimating = false;
    float animProgress = 0.0f;

    float squareColor[4] = { 1.0f, 0.0f, 0.0f, 1.0f };

    static char commandBuffer[4096] =

        "RIGHT 1\n"
        "DOWN 1\n"
        "LEFT 1\n"
        "UP 1\n"
        ;

    std::vector<GridCommand> commands;  // список команд
    bool runningCommands = false;
    int currentCommand = 0;
    float totalTime = 0.0f;
    float lastFrameTime = 0.0f;

    // параметры карты
    bool editMode = false;  // режим редактирования карты
    bool setWalls = true;   // установка стен (иначе - удаление)
    CellCoord startCell(0, 0);
    CellCoord endCell(gridSize - 1, gridSize - 1);

    // основной цикл
    bool done = false;
    while (!done)
    {
        // обработка сообщений Windows
        MSG msg;
        while (::PeekMessage(&msg, NULL, 0U, 0U, PM_REMOVE))
        {
            ::TranslateMessage(&msg);
            ::DispatchMessage(&msg);
            if (msg.message == WM_QUIT)
                done = true;
        }
        if (done)
            break;

        // расчет времени
        float currentTime = ImGui::GetTime();
        float deltaTime = currentTime - lastFrameTime;
        lastFrameTime = currentTime;
        totalTime += deltaTime;

        // обработка анимации
        if (isAnimating) {
            animProgress += ANIMATION_SPEED * deltaTime;

            if (animProgress >= 1.0f) {
                // анимация завершена, обновляем позицию
                squarePos = targetPos;
                isAnimating = false;

                if (runningCommands) {
                    bool commandCompleted = false;
                    ExecuteGridCommand(commands[currentCommand], squarePos, grid, commandCompleted);

                    if (commandCompleted) {
                        currentCommand++;
                        if (currentCommand >= commands.size()) {
                            runningCommands = false;
                        }
                    }
                }
            }
            else {
                // линейная интерполяция для плавного движения между ячейками
                animX = static_cast<float>(squarePos.x) * (1.0f - animProgress) +
                    static_cast<float>(targetPos.x) * animProgress;
                animY = static_cast<float>(squarePos.y) * (1.0f - animProgress) +
                    static_cast<float>(targetPos.y) * animProgress;
            }
        }
        // если не анимируем, но выполняем команды, выполняем следующую команду
        else if (runningCommands) {
            bool commandCompleted = false;
            ExecuteGridCommand(commands[currentCommand], squarePos, grid, commandCompleted);

            if (commands[currentCommand].type != CMD_WAIT) {
                // для всех команд, кроме WAIT, устанавливаем целевую позицию и запускаем анимацию
                targetPos = squarePos;
                isAnimating = true;
                animProgress = 0.0f;
            }
            else {
                // для команды WAIT проверяем завершение
                if (commandCompleted) {
                    currentCommand++;
                    if (currentCommand >= commands.size()) {
                        runningCommands = false;
                    }
                }
            }
        }

        FrameContext* frameCtx = WaitForNextFrameResources();
        UINT backBufferIdx = g_pSwapChain->GetCurrentBackBufferIndex();

        {
            frameCtx->CommandAllocator->Reset();
            D3D12_RESOURCE_BARRIER barrier = {};
            barrier.Type = D3D12_RESOURCE_BARRIER_TYPE_TRANSITION;
            barrier.Flags = D3D12_RESOURCE_BARRIER_FLAG_NONE;
            barrier.Transition.pResource = g_mainRenderTargetResource[backBufferIdx];
            barrier.Transition.Subresource = D3D12_RESOURCE_BARRIER_ALL_SUBRESOURCES;
            barrier.Transition.StateBefore = D3D12_RESOURCE_STATE_PRESENT;
            barrier.Transition.StateAfter = D3D12_RESOURCE_STATE_RENDER_TARGET;
            g_pd3dCommandList->Reset(frameCtx->CommandAllocator, NULL);
            g_pd3dCommandList->ResourceBarrier(1, &barrier);
            g_pd3dCommandList->OMSetRenderTargets(1, &g_mainRenderTargetDescriptor[backBufferIdx], FALSE, NULL);
            g_pd3dCommandList->SetDescriptorHeaps(1, &g_pd3dSrvDescHeap);
        }

        ImGui_ImplDX12_NewFrame();
        ImGui_ImplWin32_NewFrame();
        ImGui::NewFrame();

        // главное окно 
        {
            ImGui::SetNextWindowPos(ImVec2(10, 10), ImGuiCond_FirstUseEver);
            ImGui::SetNextWindowSize(ImVec2(600, 600), ImGuiCond_FirstUseEver);
            ImGui::Begin("Grid Map");

            // рассчёт карты
            ImVec2 contentSize = ImGui::GetContentRegionAvail();
            float gridTotalSize = gridSize * (cellSize + CELL_PADDING);
            ImVec2 gridStartPos = ImGui::GetCursorScreenPos();

            // карта
            ImDrawList* draw_list = ImGui::GetWindowDrawList();

            // отрисовка карты
            for (int y = 0; y < gridSize; y++) {
                for (int x = 0; x < gridSize; x++) {
                    // координаты ячейки
                    float cellX = gridStartPos.x + x * (cellSize + CELL_PADDING);
                    float cellY = gridStartPos.y + y * (cellSize + CELL_PADDING);

                    // цвет ячейки
                    ImU32 cellColor;
                    if (grid[y][x].isWall) {
                        cellColor = IM_COL32(100, 100, 100, 255);  // стена - серый
                    }
                    else if (grid[y][x].isStart) {
                        cellColor = IM_COL32(0, 255, 0, 255);      // начало - зелёный
                    }
                    else if (grid[y][x].isEnd) {
                        cellColor = IM_COL32(0, 0, 255, 255);      // конец - синий
                    }
                    else {
                        cellColor = IM_COL32(200, 200, 200, 255);  // светло серый - поля
                    }

                    // отрисовка ячеек
                    draw_list->AddRectFilled(
                        ImVec2(cellX, cellY),
                        ImVec2(cellX + cellSize, cellY + cellSize),
                        cellColor
                    );


                    if (editMode) {
                        ImGui::SetCursorScreenPos(ImVec2(cellX, cellY));
                        ImGui::InvisibleButton(
                            ("cell_" + std::to_string(x) + "_" + std::to_string(y)).c_str(),
                            ImVec2(cellSize, cellSize)
                        );

                        // клик по ячейке
                        if (ImGui::IsItemClicked()) {
                            if (ImGui::IsKeyDown(ImGuiKey_LeftShift)) {
                                // shift+клик стартпоз
                                CellCoord newStart(x, y);
                                if (!(grid[y][x].isWall || grid[y][x].isEnd)) {
                                    grid[startCell.y][startCell.x].isStart = false;
                                    grid[y][x].isStart = true;
                                    startCell = newStart;
                                    squarePos = newStart;
                                }
                            }
                            else if (ImGui::IsKeyDown(ImGuiKey_LeftCtrl)) {

                                CellCoord newEnd(x, y);
                                if (!(grid[y][x].isWall || grid[y][x].isStart)) {
                                    grid[endCell.y][endCell.x].isEnd = false;
                                    grid[y][x].isEnd = true;
                                    endCell = newEnd;
                                }
                            }
                            else {

                                if (!(grid[y][x].isStart || grid[y][x].isEnd)) {
                                    grid[y][x].isWall = setWalls;
                                }
                            }
                        }


                        if (ImGui::IsItemHovered()) {
                            ImGui::BeginTooltip();
                            ImGui::Text("Cell (%d, %d)", x, y);
                            ImGui::Text("Click: %s wall", setWalls ? "Add" : "Remove");
                            ImGui::Text("Shift+Click: Set start point");
                            ImGui::Text("Ctrl+Click: Set end point");
                            ImGui::EndTooltip();
                        }
                    }
                }
            }

            ImGui::SetCursorScreenPos(ImVec2(gridStartPos.x, gridStartPos.y + gridTotalSize + 10));

            float drawX, drawY;
            if (isAnimating) {
                drawX = gridStartPos.x + animX * (cellSize + CELL_PADDING);
                drawY = gridStartPos.y + animY * (cellSize + CELL_PADDING);
            }
            else {
                drawX = gridStartPos.x + squarePos.x * (cellSize + CELL_PADDING);
                drawY = gridStartPos.y + squarePos.y * (cellSize + CELL_PADDING);
            }

            float squareDrawSize = cellSize * 0.8f;
            float squareOffset = (cellSize - squareDrawSize) / 2.0f;

            ImU32 square_color = ImGui::ColorConvertFloat4ToU32(ImVec4(
                squareColor[0], squareColor[1], squareColor[2], squareColor[3]));

            draw_list->AddRectFilled(
                ImVec2(drawX + squareOffset, drawY + squareOffset),
                ImVec2(drawX + squareOffset + squareDrawSize, drawY + squareOffset + squareDrawSize),
                square_color
            );

            // управление размером сетки и ячеек
            ImGui::SetCursorScreenPos(ImVec2(gridStartPos.x, gridStartPos.y + gridTotalSize + 20));

            if (ImGui::SliderInt("Grid Size", &gridSize, 5, 20)) {

                InitializeDefaultGrid(grid, gridSize);
                startCell = CellCoord(0, 0);
                endCell = CellCoord(gridSize - 1, gridSize - 1);
                squarePos = startCell;
            }

            ImGui::SliderFloat("Cell Size", &cellSize, 20.0f, 60.0f);

            ImGui::Checkbox("Edit Mode", &editMode);
            if (editMode) {
                ImGui::SameLine();
                ImGui::Checkbox("Set Walls", &setWalls);
            }

            ImGui::Text("Square Position: (%d, %d)", squarePos.x, squarePos.y);

            if (runningCommands) {
                ImGui::Text("Running command %d/%zu", currentCommand + 1, commands.size());
                if (ImGui::Button("Stop Commands")) {
                    runningCommands = false;
                }
            }
            else {
                if (ImGui::Button("Run Commands")) {
                    commands = ParseGridCommands(commandBuffer);

                    if (!commands.empty()) {
                        runningCommands = true;
                        currentCommand = 0;
                        squarePos = startCell;
                    }
                }

                ImGui::SameLine();
                if (ImGui::Button("Move Left") && squarePos.x > 0 && !grid[squarePos.y][squarePos.x - 1].isWall) {
                    targetPos = CellCoord(squarePos.x - 1, squarePos.y);
                    isAnimating = true;
                    animProgress = 0.0f;
                }

                ImGui::SameLine();
                if (ImGui::Button("Move Right") && squarePos.x < gridSize - 1 && !grid[squarePos.y][squarePos.x + 1].isWall) {
                    targetPos = CellCoord(squarePos.x + 1, squarePos.y);
                    isAnimating = true;
                    animProgress = 0.0f;
                }

                ImGui::SameLine();
                if (ImGui::Button("Move Up") && squarePos.y > 0 && !grid[squarePos.y - 1][squarePos.x].isWall) {
                    targetPos = CellCoord(squarePos.x, squarePos.y - 1);
                    isAnimating = true;
                    animProgress = 0.0f;
                }

                ImGui::SameLine();
                if (ImGui::Button("Move Down") && squarePos.y < gridSize - 1 && !grid[squarePos.y + 1][squarePos.x].isWall) {
                    targetPos = CellCoord(squarePos.x, squarePos.y + 1);
                    isAnimating = true;
                    animProgress = 0.0f;
                }
            }

            ImGui::End();
        }

        {
            ImGui::SetNextWindowPos(ImVec2(620, 10), ImGuiCond_FirstUseEver);
            ImGui::SetNextWindowSize(ImVec2(400, 400), ImGuiCond_FirstUseEver);
            ImGui::Begin("Command Panel");

            if (ImGui::CollapsingHeader("Command Help", ImGuiTreeNodeFlags_DefaultOpen)) {
                ImGui::Text("Available commands:");
                ImGui::BulletText("RIGHT [steps] - move right by [steps] cells");
                ImGui::BulletText("LEFT [steps] - move left by [steps] cells");
                ImGui::BulletText("UP [steps] - move up by [steps] cells");
                ImGui::BulletText("DOWN [steps] - move down by [steps] cells");
                ImGui::BulletText("WAIT [steps] - wait for [steps] cycles");

            }

            ImGui::Separator();

            // редактор
            ImGui::Text("Command Editor:");
            ImGui::InputTextMultiline("##commands", commandBuffer, IM_ARRAYSIZE(commandBuffer),
                ImVec2(-FLT_MIN, ImGui::GetTextLineHeight() * 10),
                ImGuiInputTextFlags_AllowTabInput);

            ImGui::Separator();

            if (ImGui::Button("Parse Commands")) {

                commands = ParseGridCommands(commandBuffer);

                ImGui::Text("Parsed %zu commands:", commands.size());
                for (size_t i = 0; i < commands.size() && i < 10; i++) {
                    const GridCommand& cmd = commands[i];
                    switch (cmd.type) {
                    case CMD_MOVE_LEFT:
                        ImGui::Text("%zu: LEFT %d", i + 1, cmd.steps);
                        break;
                    case CMD_MOVE_RIGHT:
                        ImGui::Text("%zu: RIGHT %d", i + 1, cmd.steps);
                        break;
                    case CMD_MOVE_UP:
                        ImGui::Text("%zu: UP %d", i + 1, cmd.steps);
                        break;
                    case CMD_MOVE_DOWN:
                        ImGui::Text("%zu: DOWN %d", i + 1, cmd.steps);
                        break;
                    }
                }

                if (commands.size() > 10) {
                    ImGui::Text("... and %zu more", commands.size() - 10);
                }
            }

            ImGui::End();
        }

        ImGui::Render();

        const float clear_color_with_alpha[4] = { 0.1f, 0.1f, 0.1f, 1.0f };
        g_pd3dCommandList->ClearRenderTargetView(g_mainRenderTargetDescriptor[backBufferIdx], clear_color_with_alpha, 0, NULL);


        ImGui_ImplDX12_RenderDrawData(ImGui::GetDrawData(), g_pd3dCommandList);


        {
            D3D12_RESOURCE_BARRIER barrier = {};
            barrier.Type = D3D12_RESOURCE_BARRIER_TYPE_TRANSITION;
            barrier.Flags = D3D12_RESOURCE_BARRIER_FLAG_NONE;
            barrier.Transition.pResource = g_mainRenderTargetResource[backBufferIdx];
            barrier.Transition.Subresource = D3D12_RESOURCE_BARRIER_ALL_SUBRESOURCES;
            barrier.Transition.StateBefore = D3D12_RESOURCE_STATE_RENDER_TARGET;
            barrier.Transition.StateAfter = D3D12_RESOURCE_STATE_PRESENT;
            g_pd3dCommandList->ResourceBarrier(1, &barrier);
            g_pd3dCommandList->Close();
        }

        // команды
        g_pd3dCommandQueue->ExecuteCommandLists(1, (ID3D12CommandList* const*)&g_pd3dCommandList);

        g_pSwapChain->Present(1, 0);

        UINT64 fenceValue = g_fenceLastSignaledValue + 1;
        g_pd3dCommandQueue->Signal(g_fence, fenceValue);
        g_fenceLastSignaledValue = fenceValue;
        frameCtx->FenceValue = fenceValue;
    }

    WaitForLastSubmittedFrame();
    ImGui_ImplDX12_Shutdown();
    ImGui_ImplWin32_Shutdown();
    ImGui::DestroyContext();

    CleanupDeviceD3D();
    ::DestroyWindow(hwnd);
    ::UnregisterClassW(wc.lpszClassName, wc.hInstance);

    return 0;
}

// инициализация карты
void InitializeDefaultGrid(std::vector<std::vector<Cell>>& grid, int size) {
    grid.resize(size, std::vector<Cell>(size));

    // карта
    grid[0][0].isStart = true;
    grid[size - 1][size - 1].isEnd = true;

    if (size >= 10) {
        for (int i = 2; i < 8; i++) {
            grid[3][i].isWall = true;
        }

        for (int i = 3; i < 7; i++) {
            grid[i][7].isWall = true;
        }

        for (int i = 2; i < 6; i++) {
            grid[6][i].isWall = true;
        }
    }
}

// парсинг 
std::vector<GridCommand> ParseGridCommands(const char* commandText) {
    std::vector<GridCommand> result;
    std::istringstream stream(commandText);
    std::string line;

    while (std::getline(stream, line)) {

        if (line.empty() || line[0] == '#')
            continue;

        // разбор строки на слова
        std::istringstream lineStream(line);
        std::string command;
        lineStream >> command;

        if (command == "RIGHT") {
            int steps = 1;
            if (lineStream >> steps)
                result.push_back(GridCommand(CMD_MOVE_RIGHT, steps));
            else
                result.push_back(GridCommand(CMD_MOVE_RIGHT));
        }
        else if (command == "LEFT") {
            int steps = 1;
            if (lineStream >> steps)
                result.push_back(GridCommand(CMD_MOVE_LEFT, steps));
            else
                result.push_back(GridCommand(CMD_MOVE_LEFT));
        }
        else if (command == "UP") {
            int steps = 1;
            if (lineStream >> steps)
                result.push_back(GridCommand(CMD_MOVE_UP, steps));
            else
                result.push_back(GridCommand(CMD_MOVE_UP));
        }
        else if (command == "DOWN") {
            int steps = 1;
            if (lineStream >> steps)
                result.push_back(GridCommand(CMD_MOVE_DOWN, steps));
            else
                result.push_back(GridCommand(CMD_MOVE_DOWN));
        }
        else if (command == "WAIT") {
            int steps = 1;
            if (lineStream >> steps)
                result.push_back(GridCommand(CMD_WAIT, steps));
            else
                result.push_back(GridCommand(CMD_WAIT));
        }
    }

    return result;
}

void ExecuteGridCommand(GridCommand& cmd, CellCoord& position, const std::vector<std::vector<Cell>>& grid, bool& completed) {
    int gridSize = static_cast<int>(grid.size());

    auto isValidPosition = [&grid, gridSize](int x, int y) -> bool {
        return x >= 0 && x < gridSize && y >= 0 && y < gridSize && !grid[y][x].isWall;
        };

    completed = false;

    static int stepsExecuted = 0;
    static int waitCounter = 0;

    switch (cmd.type) {
    case CMD_MOVE_LEFT:
        if (stepsExecuted == 0) stepsExecuted = 1;

        if (isValidPosition(position.x - 1, position.y)) {
            position.x--;
            stepsExecuted++;
            if (stepsExecuted > cmd.steps) {
                completed = true;
                stepsExecuted = 0;
            }
        }
        else {

            completed = true;
            stepsExecuted = 0;
        }
        break;

    case CMD_MOVE_RIGHT:
        if (stepsExecuted == 0) stepsExecuted = 1;

        if (isValidPosition(position.x + 1, position.y)) {
            position.x++;
            stepsExecuted++;
            if (stepsExecuted > cmd.steps) {
                completed = true;
                stepsExecuted = 0;
            }
        }
        else {
            completed = true;
            stepsExecuted = 0;
        }
        break;

    case CMD_MOVE_UP:
        if (stepsExecuted == 0) stepsExecuted = 1;

        if (isValidPosition(position.x, position.y - 1)) {
            position.y--;
            stepsExecuted++;
            if (stepsExecuted > cmd.steps) {
                completed = true;
                stepsExecuted = 0;
            }
        }
        else {
            completed = true;
            stepsExecuted = 0;
        }
        break;

    case CMD_MOVE_DOWN:
        if (stepsExecuted == 0) stepsExecuted = 1;

        if (isValidPosition(position.x, position.y + 1)) {
            position.y++;
            stepsExecuted++;
            if (stepsExecuted > cmd.steps) {
                completed = true;
                stepsExecuted = 0;
            }
        }
        else {
            completed = true;
            stepsExecuted = 0;
        }
        break;

    case CMD_NONE:
    default:
        completed = true;
        break;
    }
}

LRESULT WINAPI WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam)
{
    if (ImGui_ImplWin32_WndProcHandler(hWnd, msg, wParam, lParam))
        return true;

    switch (msg)
    {
    case WM_SIZE:
        if (g_pd3dDevice != NULL && wParam != SIZE_MINIMIZED)
        {
            WaitForLastSubmittedFrame();
            CleanupRenderTarget();
            g_pSwapChain->ResizeBuffers(0, (UINT)LOWORD(lParam), (UINT)HIWORD(lParam), DXGI_FORMAT_UNKNOWN, DXGI_SWAP_CHAIN_FLAG_FRAME_LATENCY_WAITABLE_OBJECT);
            CreateRenderTarget();
        }
        return 0;
    case WM_SYSCOMMAND:
        if ((wParam & 0xfff0) == SC_KEYMENU)
            return 0;
        break;
    case WM_DESTROY:
        ::PostQuitMessage(0);
        return 0;
    }
    return ::DefWindowProcW(hWnd, msg, wParam, lParam);
}

bool CreateDeviceD3D(HWND hWnd)
{

    D3D_FEATURE_LEVEL featureLevel = D3D_FEATURE_LEVEL_11_0;
    if (D3D12CreateDevice(NULL, featureLevel, IID_PPV_ARGS(&g_pd3dDevice)) != S_OK)
        return false;

    // очередь 
    {
        D3D12_COMMAND_QUEUE_DESC desc = {};
        desc.Type = D3D12_COMMAND_LIST_TYPE_DIRECT;
        desc.Flags = D3D12_COMMAND_QUEUE_FLAG_NONE;
        desc.NodeMask = 1;
        if (g_pd3dDevice->CreateCommandQueue(&desc, IID_PPV_ARGS(&g_pd3dCommandQueue)) != S_OK)
            return false;
    }

    // обмен
    {
        DXGI_SWAP_CHAIN_DESC1 sd;
        ZeroMemory(&sd, sizeof(sd));
        sd.BufferCount = NUM_FRAMES_IN_FLIGHT;
        sd.Width = 0;
        sd.Height = 0;
        sd.Format = DXGI_FORMAT_R8G8B8A8_UNORM;
        sd.Flags = DXGI_SWAP_CHAIN_FLAG_FRAME_LATENCY_WAITABLE_OBJECT;
        sd.BufferUsage = DXGI_USAGE_RENDER_TARGET_OUTPUT;
        sd.SampleDesc.Count = 1;
        sd.SampleDesc.Quality = 0;
        sd.SwapEffect = DXGI_SWAP_EFFECT_FLIP_DISCARD;
        sd.AlphaMode = DXGI_ALPHA_MODE_UNSPECIFIED;
        sd.Scaling = DXGI_SCALING_STRETCH;
        sd.Stereo = FALSE;

        IDXGIFactory4* dxgiFactory = NULL;
        IDXGISwapChain1* swapChain1 = NULL;
        if (CreateDXGIFactory1(IID_PPV_ARGS(&dxgiFactory)) != S_OK)
            return false;
        if (dxgiFactory->CreateSwapChainForHwnd(g_pd3dCommandQueue, hWnd, &sd, NULL, NULL, &swapChain1) != S_OK)
            return false;
        if (swapChain1->QueryInterface(IID_PPV_ARGS(&g_pSwapChain)) != S_OK)
            return false;
        g_pSwapChain->SetMaximumFrameLatency(NUM_FRAMES_IN_FLIGHT);
        g_hSwapChainWaitableObject = g_pSwapChain->GetFrameLatencyWaitableObject();
        dxgiFactory->Release();
        swapChain1->Release();
    }


    {

        D3D12_DESCRIPTOR_HEAP_DESC desc = {};
        desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_RTV;
        desc.NumDescriptors = NUM_FRAMES_IN_FLIGHT;
        desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_NONE;
        desc.NodeMask = 1;
        if (g_pd3dDevice->CreateDescriptorHeap(&desc, IID_PPV_ARGS(&g_pd3dRtvDescHeap)) != S_OK)
            return false;

        SIZE_T rtvDescriptorSize = g_pd3dDevice->GetDescriptorHandleIncrementSize(D3D12_DESCRIPTOR_HEAP_TYPE_RTV);
        D3D12_CPU_DESCRIPTOR_HANDLE rtvHandle = g_pd3dRtvDescHeap->GetCPUDescriptorHandleForHeapStart();
        for (UINT i = 0; i < NUM_FRAMES_IN_FLIGHT; i++)
        {
            g_mainRenderTargetDescriptor[i] = rtvHandle;
            rtvHandle.ptr += rtvDescriptorSize;
        }

        desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV;
        desc.NumDescriptors = 1;
        desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE;
        if (g_pd3dDevice->CreateDescriptorHeap(&desc, IID_PPV_ARGS(&g_pd3dSrvDescHeap)) != S_OK)
            return false;
    }


    {
        for (UINT i = 0; i < NUM_FRAMES_IN_FLIGHT; i++)
            if (g_pd3dDevice->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&g_frameContext[i].CommandAllocator)) != S_OK)
                return false;

        if (g_pd3dDevice->CreateCommandList(0, D3D12_COMMAND_LIST_TYPE_DIRECT, g_frameContext[0].CommandAllocator, NULL, IID_PPV_ARGS(&g_pd3dCommandList)) != S_OK ||
            g_pd3dCommandList->Close() != S_OK)
            return false;
    }

    // синхронизация
    {
        if (g_pd3dDevice->CreateFence(0, D3D12_FENCE_FLAG_NONE, IID_PPV_ARGS(&g_fence)) != S_OK)
            return false;

        g_fenceEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
        if (g_fenceEvent == NULL)
            return false;

        WaitForLastSubmittedFrame();
    }

    // рендер
    CreateRenderTarget();

    return true;
}

void CleanupDeviceD3D()
{
    CleanupRenderTarget();

    if (g_pSwapChain) { g_pSwapChain->Release(); g_pSwapChain = NULL; }
    if (g_hSwapChainWaitableObject) { CloseHandle(g_hSwapChainWaitableObject); g_hSwapChainWaitableObject = NULL; }
    for (UINT i = 0; i < NUM_FRAMES_IN_FLIGHT; i++)
        if (g_frameContext[i].CommandAllocator) { g_frameContext[i].CommandAllocator->Release(); g_frameContext[i].CommandAllocator = NULL; }
    if (g_pd3dCommandQueue) { g_pd3dCommandQueue->Release(); g_pd3dCommandQueue = NULL; }
    if (g_pd3dCommandList) { g_pd3dCommandList->Release(); g_pd3dCommandList = NULL; }
    if (g_pd3dRtvDescHeap) { g_pd3dRtvDescHeap->Release(); g_pd3dRtvDescHeap = NULL; }
    if (g_pd3dSrvDescHeap) { g_pd3dSrvDescHeap->Release(); g_pd3dSrvDescHeap = NULL; }
    if (g_fence) { g_fence->Release(); g_fence = NULL; }
    if (g_fenceEvent) { CloseHandle(g_fenceEvent); g_fenceEvent = NULL; }
    if (g_pd3dDevice) { g_pd3dDevice->Release(); g_pd3dDevice = NULL; }
}

void CreateRenderTarget()
{
    for (UINT i = 0; i < NUM_FRAMES_IN_FLIGHT; i++)
    {
        ID3D12Resource* pBackBuffer = NULL;
        g_pSwapChain->GetBuffer(i, IID_PPV_ARGS(&pBackBuffer));
        g_pd3dDevice->CreateRenderTargetView(pBackBuffer, NULL, g_mainRenderTargetDescriptor[i]);
        g_mainRenderTargetResource[i] = pBackBuffer;
    }
}

void CleanupRenderTarget()
{
    WaitForLastSubmittedFrame();
    for (UINT i = 0; i < NUM_FRAMES_IN_FLIGHT; i++)
        if (g_mainRenderTargetResource[i]) { g_mainRenderTargetResource[i]->Release(); g_mainRenderTargetResource[i] = NULL; }
}

void WaitForLastSubmittedFrame()
{
    FrameContext* frameCtx = &g_frameContext[g_frameIndex % NUM_FRAMES_IN_FLIGHT];
    UINT64 fenceValue = frameCtx->FenceValue;
    if (fenceValue == 0)
        return;

    frameCtx->FenceValue = 0;
    if (g_fence->GetCompletedValue() >= fenceValue)
        return;

    g_fence->SetEventOnCompletion(fenceValue, g_fenceEvent);
    WaitForSingleObject(g_fenceEvent, INFINITE);
}

FrameContext* WaitForNextFrameResources()
{
    UINT nextFrameIndex = g_frameIndex + 1;
    g_frameIndex = nextFrameIndex;

    HANDLE waitableObjects[] = { g_hSwapChainWaitableObject, NULL };
    DWORD numWaitableObjects = 1;

    FrameContext* frameCtx = &g_frameContext[nextFrameIndex % NUM_FRAMES_IN_FLIGHT];
    UINT64 fenceValue = frameCtx->FenceValue;
    if (fenceValue != 0)
    {
        frameCtx->FenceValue = 0;
        g_fence->SetEventOnCompletion(fenceValue, g_fenceEvent);
        waitableObjects[1] = g_fenceEvent;
        numWaitableObjects = 2;
    }

    WaitForMultipleObjects(numWaitableObjects, waitableObjects, TRUE, INFINITE);
    return frameCtx;
}