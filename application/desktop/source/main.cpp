#include <imgui_impl_dx12.cpp>
#include <exception>
#include <stdio.h>
#include <fstream>
#include "../include/frameContext.h"
#include "../include/cell.h"
#include "../include/gridCommand.h"
#include "../include/cellCord.h"

const int NUM_FRAMES_IN_FLIGHT = 3;
const int DEFAULT_GRID_SIZE = 10;
const float CELL_PADDING = 2.0f;
const float ANIMATION_SPEED = 5.0f;
FrameContext g_frameContext[NUM_FRAMES_IN_FLIGHT] = {};
UINT g_frameIndex = 0;
ID3D12Device* g_pd3dDevice = NULL;
ID3D12DescriptorHeap* g_pd3dRtvDescHeap = NULL;
ID3D12DescriptorHeap* g_pd3dSrvDescHeap = NULL;
ID3D12CommandQueue* g_pd3dCommandQueue = NULL;
ID3D12GraphicsCommandList* g_pd3dCommandList = NULL;
ID3D12Fence* g_fence = NULL;
HANDLE g_fenceEvent = NULL;
UINT64 g_fenceLastSignaledValue = 0;
IDXGISwapChain3* g_pSwapChain = NULL;
HANDLE g_hSwapChainWaitableObject = NULL;
ID3D12Resource* g_mainRenderTargetResource[NUM_FRAMES_IN_FLIGHT] = {};
D3D12_CPU_DESCRIPTOR_HANDLE g_mainRenderTargetDescriptor[NUM_FRAMES_IN_FLIGHT] = {};
Cell g_grid[DEFAULT_GRID_SIZE * 2][DEFAULT_GRID_SIZE * 2];
int g_gridSize = DEFAULT_GRID_SIZE;
GridCommand g_commands[100];  // ћассив команд
int g_commandCount = 0;
char g_commandBuffer[4096] = "RIGHT 1\nDOWN 1\nLEFT 1\nUP 1\n";
char g_saveError[256] = ""; // Ѕуфер дл€ хранени€ сообщений об ошибках при сохранении

bool CreateDeviceD3D(HWND hWnd);
void CleanupDeviceD3D();
void CreateRenderTarget();
void CleanupRenderTarget();
void WaitForLastSubmittedFrame();
FrameContext* WaitForNextFrameResources();
LRESULT WINAPI WndProc(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);
void ParseGridCommands();
void ExecuteGridCommand(GridCommand& cmd, CellCoord& position, bool& completed);
void InitializeDefaultGrid(int size);
char* IntToStr(int value, char* buffer);
bool SaveGridMapToFile(const char* filename, int gridSize, Cell grid[][DEFAULT_GRID_SIZE * 2], CellCoord startPos, CellCoord endPos);
bool LoadGridMapFromFile(const char* filename, int& gridSize, Cell grid[][DEFAULT_GRID_SIZE * 2], CellCoord& startPos, CellCoord& endPos);

extern IMGUI_IMPL_API LRESULT ImGui_ImplWin32_WndProcHandler(HWND hWnd, UINT msg, WPARAM wParam, LPARAM lParam);

bool SaveGridMapToFile(const char* filename, int gridSize, Cell grid[][DEFAULT_GRID_SIZE * 2],
    CellCoord startPos, CellCoord endPos) {
    std::ofstream outFile(filename, std::ios::binary);
    if (!outFile.is_open()) {
        snprintf(g_saveError, sizeof(g_saveError), "Cannot open file: %s", filename);
        return false;
    }

    try {
        const char signature[] = "GRIDMAP";
        outFile.write(signature, 7);

        unsigned char version = 1;
        outFile.write(reinterpret_cast<const char*>(&version), sizeof(version));

        outFile.write(reinterpret_cast<const char*>(&gridSize), sizeof(gridSize));

        outFile.write(reinterpret_cast<const char*>(&startPos.x), sizeof(startPos.x));
        outFile.write(reinterpret_cast<const char*>(&startPos.y), sizeof(startPos.y));

        outFile.write(reinterpret_cast<const char*>(&endPos.x), sizeof(endPos.x));
        outFile.write(reinterpret_cast<const char*>(&endPos.y), sizeof(endPos.y));

        for (int y = 0; y < gridSize; y++) {
            for (int x = 0; x < gridSize; x++) {
                unsigned char cellData = 0;
                if (grid[y][x].isWall) cellData |= 0x01;
                if (grid[y][x].isStart) cellData |= 0x02;
                if (grid[y][x].isEnd) cellData |= 0x04;
                outFile.write(reinterpret_cast<const char*>(&cellData), sizeof(cellData));
            }
        }

        outFile.close();
        g_saveError[0] = '\0';
        return true;
    }
    catch (const std::exception& e) {
        snprintf(g_saveError, sizeof(g_saveError), "Map error: %s", e.what());
        outFile.close();
        return false;
    }
}

bool LoadGridMapFromFile(const char* filename, int& gridSize, Cell grid[][DEFAULT_GRID_SIZE * 2],
    CellCoord& startPos, CellCoord& endPos) {
    std::ifstream inFile(filename, std::ios::binary);
    if (!inFile.is_open()) {
        snprintf(g_saveError, sizeof(g_saveError), "Cannot open file: %s", filename);
        return false;
    }

    try {
        char signature[8] = { 0 };
        inFile.read(signature, 7);
        if (strcmp(signature, "GRIDMAP") != 0) {
            snprintf(g_saveError, sizeof(g_saveError), "Incorrect format");
            inFile.close();
            return false;
        }

        unsigned char version;
        inFile.read(reinterpret_cast<char*>(&version), sizeof(version));
        if (version != 1) {
            snprintf(g_saveError, sizeof(g_saveError), "Unsupported file version: %d", (int)version);
            inFile.close();
            return false;
        }

        int fileGridSize;
        inFile.read(reinterpret_cast<char*>(&fileGridSize), sizeof(fileGridSize));

        if (fileGridSize > DEFAULT_GRID_SIZE * 2) {
            snprintf(g_saveError, sizeof(g_saveError), "Grid size exceeds maximum (%d > %d)",
                fileGridSize, DEFAULT_GRID_SIZE * 2);
            inFile.close();
            return false;
        }

        gridSize = fileGridSize;

        inFile.read(reinterpret_cast<char*>(&startPos.x), sizeof(startPos.x));
        inFile.read(reinterpret_cast<char*>(&startPos.y), sizeof(startPos.y));

        inFile.read(reinterpret_cast<char*>(&endPos.x), sizeof(endPos.x));
        inFile.read(reinterpret_cast<char*>(&endPos.y), sizeof(endPos.y));

        for (int y = 0; y < DEFAULT_GRID_SIZE * 2; y++) {
            for (int x = 0; x < DEFAULT_GRID_SIZE * 2; x++) {
                grid[y][x].isWall = false;
                grid[y][x].isStart = false;
                grid[y][x].isEnd = false;
            }
        }

        for (int y = 0; y < gridSize; y++) {
            for (int x = 0; x < gridSize; x++) {
                unsigned char cellData;
                inFile.read(reinterpret_cast<char*>(&cellData), sizeof(cellData));

                grid[y][x].isWall = (cellData & 0x01) != 0;
                grid[y][x].isStart = (cellData & 0x02) != 0;
                grid[y][x].isEnd = (cellData & 0x04) != 0;
            }
        }

        inFile.close();
        g_saveError[0] = '\0';
        return true;
    }
    catch (const std::exception& e) {
        snprintf(g_saveError, sizeof(g_saveError), "Read Error: %s", e.what());
        inFile.close();
        return false;
    }
}
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

    InitializeDefaultGrid(DEFAULT_GRID_SIZE);

    float cellSize = 40.0f;
    // позици€
    CellCoord squarePos(0, 0);
    CellCoord targetPos = squarePos;
    float animX = 0.0f;
    float animY = 0.0f;
    bool isAnimating = false;
    float animProgress = 0.0f;

    float squareColor[4] = { 1.0f, 0.0f, 0.0f, 1.0f };

    ParseGridCommands();
    bool runningCommands = false;
    int currentCommand = 0;
    float totalTime = 0.0f;
    float lastFrameTime = 0.0f;

    // параметры карты
    bool editMode = false;  // режим редактировани€ карты
    bool setWalls = true;   // установка стен (иначе - удаление)
    CellCoord startCell(0, 0);
    CellCoord endCell(g_gridSize - 1, g_gridSize - 1);

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
                // обновление позиции
                squarePos = targetPos;
                isAnimating = false;

                // проверка на баг
                if (runningCommands && currentCommand < g_commandCount) {
                    currentCommand++;
                    if (currentCommand >= g_commandCount) {
                        runningCommands = false;
                    }
                }
            }
            else {
                animX = static_cast<float>(squarePos.x) * (1.0f - animProgress) +
                    static_cast<float>(targetPos.x) * animProgress;
                animY = static_cast<float>(squarePos.y) * (1.0f - animProgress) +
                    static_cast<float>(targetPos.y) * animProgress;
            }
        }
        else if (runningCommands && currentCommand < g_commandCount) {
            bool commandCompleted = false;

            // обновление позиции
            ExecuteGridCommand(g_commands[currentCommand], squarePos, commandCompleted);

            targetPos = squarePos;
            isAnimating = true;
            animProgress = 0.0f;
        }
        // если не анимируем, но выполн€ем команды, выполн€ем следующую команду
        else if (runningCommands) {
            bool commandCompleted = false;
            ExecuteGridCommand(g_commands[currentCommand], squarePos, commandCompleted);

            targetPos = squarePos;
            isAnimating = true;
            animProgress = 0.0f;
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

            // рассчЄт карты
            ImVec2 contentSize = ImGui::GetContentRegionAvail();
            float gridTotalSize = g_gridSize * (cellSize + CELL_PADDING);
            ImVec2 gridStartPos = ImGui::GetCursorScreenPos();

            // карта
            ImDrawList* draw_list = ImGui::GetWindowDrawList();

            // отрисовка карты
            for (int y = 0; y < g_gridSize; y++) {
                for (int x = 0; x < g_gridSize; x++) {
                    // координаты €чейки
                    float cellX = gridStartPos.x + x * (cellSize + CELL_PADDING);
                    float cellY = gridStartPos.y + y * (cellSize + CELL_PADDING);

                    // цвет €чейки
                    ImU32 cellColor;
                    if (g_grid[y][x].isWall) {
                        cellColor = IM_COL32(100, 100, 100, 255);  // стена - серый
                    }
                    else if (g_grid[y][x].isStart) {
                        cellColor = IM_COL32(0, 255, 0, 255);      // начало - зелЄный
                    }
                    else if (g_grid[y][x].isEnd) {
                        cellColor = IM_COL32(0, 0, 255, 255);      // конец - синий
                    }
                    else {
                        cellColor = IM_COL32(200, 200, 200, 255);  // светло серый - пол€
                    }

                    // отрисовка €чеек
                    draw_list->AddRectFilled(
                        ImVec2(cellX, cellY),
                        ImVec2(cellX + cellSize, cellY + cellSize),
                        cellColor
                    );

                    if (editMode) {
                        ImGui::SetCursorScreenPos(ImVec2(cellX, cellY));

                        char btnId[32];
                        char* p = btnId;
                        *p++ = 'c';
                        *p++ = 'e';
                        *p++ = 'l';
                        *p++ = 'l';
                        *p++ = '_';
                        p = IntToStr(x, p);
                        *p++ = '_';
                        p = IntToStr(y, p);
                        *p = '\0';

                        ImGui::InvisibleButton(btnId, ImVec2(cellSize, cellSize));

                        // клик по €чейке
                        if (ImGui::IsItemClicked()) {
                            if (ImGui::IsKeyDown(ImGuiKey_LeftShift)) {
                                // shift+клик стартпоз
                                CellCoord newStart(x, y);
                                if (!(g_grid[y][x].isWall || g_grid[y][x].isEnd)) {
                                    g_grid[startCell.y][startCell.x].isStart = false;
                                    g_grid[y][x].isStart = true;
                                    startCell = newStart;
                                    squarePos = newStart;
                                }
                            }
                            else if (ImGui::IsKeyDown(ImGuiKey_LeftCtrl)) {
                                CellCoord newEnd(x, y);
                                if (!(g_grid[y][x].isWall || g_grid[y][x].isStart)) {
                                    g_grid[endCell.y][endCell.x].isEnd = false;
                                    g_grid[y][x].isEnd = true;
                                    endCell = newEnd;
                                }
                            }
                            else {
                                if (!(g_grid[y][x].isStart || g_grid[y][x].isEnd)) {
                                    g_grid[y][x].isWall = setWalls;
                                }
                            }
                        }

                        if (ImGui::IsItemHovered()) {
                            ImGui::BeginTooltip();
                            char posBuffer[32];
                            char* p = posBuffer;
                            *p++ = 'C';
                            *p++ = 'e';
                            *p++ = 'l';
                            *p++ = 'l';
                            *p++ = ' ';
                            *p++ = '(';
                            p = IntToStr(x, p);
                            *p++ = ',';
                            *p++ = ' ';
                            p = IntToStr(y, p);
                            *p++ = ')';
                            *p = '\0';
                            ImGui::Text("%s", posBuffer);

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

            // управление размером сетки и €чеек
            ImGui::SetCursorScreenPos(ImVec2(gridStartPos.x, gridStartPos.y + gridTotalSize + 20));

            if (ImGui::SliderInt("Grid Size", &g_gridSize, 5, 20)) {
                InitializeDefaultGrid(g_gridSize);
                startCell = CellCoord(0, 0);
                endCell = CellCoord(g_gridSize - 1, g_gridSize - 1);
                squarePos = startCell;
            }

            ImGui::SliderFloat("Cell Size", &cellSize, 20.0f, 60.0f);

            ImGui::Checkbox("Edit Mode", &editMode);
            if (editMode) {
                ImGui::SameLine();
                ImGui::Checkbox("Set Walls", &setWalls);
            }

            char posText[64];
            char* p = posText;
            *p++ = 'S';
            *p++ = 'q';
            *p++ = 'u';
            *p++ = 'a';
            *p++ = 'r';
            *p++ = 'e';
            *p++ = ' ';
            *p++ = 'P';
            *p++ = 'o';
            *p++ = 's';
            *p++ = 'i';
            *p++ = 't';
            *p++ = 'i';
            *p++ = 'o';
            *p++ = 'n';
            *p++ = ':';
            *p++ = ' ';
            *p++ = '(';
            p = IntToStr(squarePos.x, p);
            *p++ = ',';
            *p++ = ' ';
            p = IntToStr(squarePos.y, p);
            *p++ = ')';
            *p = '\0';

            ImGui::Text("%s", posText);

            if (runningCommands) {
                char cmdText[64];
                char* p = cmdText;
                *p++ = 'R';
                *p++ = 'u';
                *p++ = 'n';
                *p++ = 'n';
                *p++ = 'i';
                *p++ = 'n';
                *p++ = 'g';
                *p++ = ' ';
                *p++ = 'c';
                *p++ = 'o';
                *p++ = 'm';
                *p++ = 'm';
                *p++ = 'a';
                *p++ = 'n';
                *p++ = 'd';
                *p++ = ' ';
                p = IntToStr(currentCommand + 1, p);
                *p++ = '/';
                p = IntToStr(g_commandCount, p);
                *p = '\0';

                ImGui::Text("%s", cmdText);

                if (ImGui::Button("Stop Commands")) {
                    runningCommands = false;
                }
            }
            else {
                if (ImGui::Button("Run Commands")) {
                    ParseGridCommands();

                    if (g_commandCount > 0) {
                        runningCommands = true;
                        currentCommand = 0;
                        squarePos = startCell;
                    }
                }

                ImGui::SameLine();
                if (ImGui::Button("Move Left") && squarePos.x > 0 && !g_grid[squarePos.y][squarePos.x - 1].isWall) {
                    targetPos = CellCoord(squarePos.x - 1, squarePos.y);
                    isAnimating = true;
                    animProgress = 0.0f;
                }

                ImGui::SameLine();
                if (ImGui::Button("Move Right") && squarePos.x < g_gridSize - 1 && !g_grid[squarePos.y][squarePos.x + 1].isWall) {
                    targetPos = CellCoord(squarePos.x + 1, squarePos.y);
                    isAnimating = true;
                    animProgress = 0.0f;
                }

                ImGui::SameLine();
                if (ImGui::Button("Move Up") && squarePos.y > 0 && !g_grid[squarePos.y - 1][squarePos.x].isWall) {
                    targetPos = CellCoord(squarePos.x, squarePos.y - 1);
                    isAnimating = true;
                    animProgress = 0.0f;
                }

                ImGui::SameLine();
                if (ImGui::Button("Move Down") && squarePos.y < g_gridSize - 1 && !g_grid[squarePos.y + 1][squarePos.x].isWall) {
                    targetPos = CellCoord(squarePos.x, squarePos.y + 1);
                    isAnimating = true;
                    animProgress = 0.0f;
                }
            }

            ImGui::End();
        }


ImGui::Separator();

if (ImGui::Button("Save Map")) {
    char filename[MAX_PATH] = "grid_map.gmap";
    
    OPENFILENAMEA ofn;
    ZeroMemory(&ofn, sizeof(ofn));
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = hwnd;
    ofn.lpstrFilter = "Grid Map Files (*.gmap)\0*.gmap\0All Files (*.*)\0*.*\0";
    ofn.lpstrFile = filename;
    ofn.nMaxFile = sizeof(filename);
    ofn.lpstrTitle = "Save Grid Map";
    ofn.Flags = OFN_OVERWRITEPROMPT;
    ofn.lpstrDefExt = "gmap";

    if (GetSaveFileNameA(&ofn)) {
        bool success = SaveGridMapToFile(filename, g_gridSize, g_grid, startCell, endCell);
        if (success) {
            snprintf(g_saveError, sizeof(g_saveError), "Map saved successfully: %s", filename);
        }
    }
}

ImGui::SameLine();
if (ImGui::Button("Load Map")) {
    char filename[MAX_PATH] = "";
    
    OPENFILENAMEA ofn;
    ZeroMemory(&ofn, sizeof(ofn));
    ofn.lStructSize = sizeof(ofn);
    ofn.hwndOwner = hwnd;
    ofn.lpstrFilter = "Grid Map Files (*.gmap)\0*.gmap\0All Files (*.*)\0*.*\0";
    ofn.lpstrFile = filename;
    ofn.nMaxFile = sizeof(filename);
    ofn.lpstrTitle = "Load Grid Map";
    ofn.Flags = OFN_FILEMUSTEXIST | OFN_PATHMUSTEXIST;
    ofn.lpstrDefExt = "gmap";

    if (GetOpenFileNameA(&ofn)) {
        bool success = LoadGridMapFromFile(filename, g_gridSize, g_grid, startCell, endCell);
        if (success) {
            snprintf(g_saveError, sizeof(g_saveError), "Map loaded successfully: %s", filename);
            squarePos = startCell; 
            

        }
    }
}

if (g_saveError[0] != '\0') {
    ImGui::TextWrapped("%s", g_saveError);
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
            }

            ImGui::Separator();

            // редактор
            ImGui::Text("Command Editor:");
            ImGui::InputTextMultiline("##commands", g_commandBuffer, IM_ARRAYSIZE(g_commandBuffer),
                ImVec2(-FLT_MIN, ImGui::GetTextLineHeight() * 10),
                ImGuiInputTextFlags_AllowTabInput);

            ImGui::Separator();

            if (ImGui::Button("Parse Commands")) {
                ParseGridCommands();

                ImGui::Text("Parsed %d commands:", g_commandCount);
                for (int i = 0; i < g_commandCount && i < 10; i++) {
                    const GridCommand& cmd = g_commands[i];
                    char cmdText[64];
                    char* p = cmdText;
                    p = IntToStr(i + 1, p);
                    *p++ = ':';
                    *p++ = ' ';

                    switch (cmd.type) {
                    case CMD_MOVE_LEFT:
                        *p++ = 'L';
                        *p++ = 'E';
                        *p++ = 'F';
                        *p++ = 'T';
                        *p++ = ' ';
                        p = IntToStr(cmd.steps, p);
                        break;
                    case CMD_MOVE_RIGHT:
                        *p++ = 'R';
                        *p++ = 'I';
                        *p++ = 'G';
                        *p++ = 'H';
                        *p++ = 'T';
                        *p++ = ' ';
                        p = IntToStr(cmd.steps, p);
                        break;
                    case CMD_MOVE_UP:
                        *p++ = 'U';
                        *p++ = 'P';
                        *p++ = ' ';
                        p = IntToStr(cmd.steps, p);
                        break;
                    case CMD_MOVE_DOWN:
                        *p++ = 'D';
                        *p++ = 'O';
                        *p++ = 'W';
                        *p++ = 'N';
                        *p++ = ' ';
                        p = IntToStr(cmd.steps, p);
                        break;
                    }
                    *p = '\0';
                    ImGui::Text("%s", cmdText);
                }

                if (g_commandCount > 10) {
                    char moreText[32];
                    char* p = moreText;
                    *p++ = '.';
                    *p++ = '.';
                    *p++ = '.';
                    *p++ = ' ';
                    *p++ = 'a';
                    *p++ = 'n';
                    *p++ = 'd';
                    *p++ = ' ';
                    p = IntToStr(g_commandCount - 10, p);
                    *p++ = ' ';
                    *p++ = 'm';
                    *p++ = 'o';
                    *p++ = 'r';
                    *p++ = 'e';
                    *p = '\0';
                    ImGui::Text("%s", moreText);
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

char* IntToStr(int value, char* buffer) {
    if (value == 0) {
        *buffer++ = '0';
        return buffer;
    }

    char temp[16];
    int tempIdx = 0;
    bool negative = false;

    if (value < 0) {
        negative = true;
        value = -value;
    }

    while (value > 0) {
        temp[tempIdx++] = '0' + (value % 10);
        value /= 10;
    }

    if (negative) {
        *buffer++ = '-';
    }

    while (tempIdx > 0) {
        *buffer++ = temp[--tempIdx];
    }

    return buffer;
}

// инициализаци€ карты
void InitializeDefaultGrid(int size) {
    if (size < 5) size = 5;

    for (int y = 0; y < size; y++) {
        for (int x = 0; x < size; x++) {
            g_grid[y][x].isWall = false;
            g_grid[y][x].isStart = false;
            g_grid[y][x].isEnd = false;
        }
    }

    g_grid[0][0].isStart = true;
    g_grid[size - 1][size - 1].isEnd = true;
    g_gridSize = size;
}

bool StrEquals(const char* str1, const char* str2) {
    while (*str1 && *str2) {
        if (*str1 != *str2) return false;
        str1++;
        str2++;
    }
    return *str1 == *str2;
}

void GetNextWord(const char** ptr, char* word) {

    while (**ptr && (**ptr == ' ' || **ptr == '\t')) {
        (*ptr)++;
    }

    char* dest = word;
    while (**ptr && **ptr != ' ' && **ptr != '\t' && **ptr != '\n' && **ptr != '\r') {
        *dest++ = **ptr;
        (*ptr)++;
    }
    *dest = '\0';
}

int StrToInt(const char* str) {
    int result = 0;
    bool negative = false;

    if (*str == '-') {
        negative = true;
        str++;
    }

    while (*str >= '0' && *str <= '9') {
        result = result * 10 + (*str - '0');
        str++;
    }

    return negative ? -result : result;
}

// парсинг 
void ParseGridCommands() {
    g_commandCount = 0;
    const char* ptr = g_commandBuffer;

    char line[256];
    char word[32];

    while (*ptr && g_commandCount < 100) {

        char* linePtr = line;
        while (*ptr && *ptr != '\n' && *ptr != '\r') {
            *linePtr++ = *ptr++;
        }
        *linePtr = '\0';

        while (*ptr == '\n' || *ptr == '\r') {
            ptr++;
        }

        if (line[0] == '\0' || line[0] == '#') {
            continue;
        }


        const char* lineReader = line;
        GetNextWord(&lineReader, word);

        if (StrEquals(word, "RIGHT")) {
            GetNextWord(&lineReader, word);
            int steps = word[0] ? StrToInt(word) : 1;
            g_commands[g_commandCount++] = GridCommand(CMD_MOVE_RIGHT, steps);
        }
        else if (StrEquals(word, "LEFT")) {
            GetNextWord(&lineReader, word);
            int steps = word[0] ? StrToInt(word) : 1;
            g_commands[g_commandCount++] = GridCommand(CMD_MOVE_LEFT, steps);
        }
        else if (StrEquals(word, "UP")) {
            GetNextWord(&lineReader, word);
            int steps = word[0] ? StrToInt(word) : 1;
            g_commands[g_commandCount++] = GridCommand(CMD_MOVE_UP, steps);
        }
        else if (StrEquals(word, "DOWN")) {
            GetNextWord(&lineReader, word);
            int steps = word[0] ? StrToInt(word) : 1;
            g_commands[g_commandCount++] = GridCommand(CMD_MOVE_DOWN, steps);
        }
    }
}

void ExecuteGridCommand(GridCommand& cmd, CellCoord& position, bool& completed) {
    auto isCellWall = [](int y, int x) -> bool {
        if (y < 0 || y >= g_gridSize) return true;
        if (x < 0 || x >= g_gridSize) return true;
        return g_grid[y][x].isWall;
        };

    completed = false;

    switch (cmd.type) {
    case CMD_MOVE_LEFT:
    {
        int targetX = position.x;
        for (int step = 0; step < cmd.steps && targetX > 0; step++) {
            if (!isCellWall(position.y, targetX - 1)) {
                targetX--;
            }
            else {
                break;
            }
        }
        position.x = targetX;
        completed = true;
    }
    break;

    case CMD_MOVE_RIGHT:
    {
        int targetX = position.x;
        for (int step = 0; step < cmd.steps && targetX < g_gridSize - 1; step++) {
            if (!isCellWall(position.y, targetX + 1)) {
                targetX++;
            }
            else {
                break;
            }
        }
        position.x = targetX;
        completed = true;
    }
    break;

    case CMD_MOVE_UP:
    {
        int targetY = position.y;
        for (int step = 0; step < cmd.steps && targetY > 0; step++) {
            if (!isCellWall(targetY - 1, position.x)) {
                targetY--;
            }
            else {
                break;
            }
        }
        position.y = targetY;
        completed = true;
    }
    break;

    case CMD_MOVE_DOWN:
    {
        int targetY = position.y;
        for (int step = 0; step < cmd.steps && targetY < g_gridSize - 1; step++) {
            if (!isCellWall(targetY + 1, position.x)) {
                targetY++;
            }
            else {
                break;
            }
        }
        position.y = targetY;
        completed = true;
    }
    break;

    case CMD_NONE:
    default:
        completed = true;
        break;
    }

    if (position.x < 0) position.x = 0;
    if (position.x >= g_gridSize) position.x = g_gridSize - 1;
    if (position.y < 0) position.y = 0;
    if (position.y >= g_gridSize) position.y = g_gridSize - 1;
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
        for (UINT i = 0; i < NUM_FRAMES_IN_FLIGHT; i++) {
            g_mainRenderTargetDescriptor[i] = rtvHandle;
            rtvHandle.ptr += rtvDescriptorSize;
        }
    }

    {
        D3D12_DESCRIPTOR_HEAP_DESC desc = {};
        desc.Type = D3D12_DESCRIPTOR_HEAP_TYPE_CBV_SRV_UAV;
        desc.NumDescriptors = 1;
        desc.Flags = D3D12_DESCRIPTOR_HEAP_FLAG_SHADER_VISIBLE;
        if (g_pd3dDevice->CreateDescriptorHeap(&desc, IID_PPV_ARGS(&g_pd3dSrvDescHeap)) != S_OK)
            return false;
    }

    {
        for (UINT i = 0; i < NUM_FRAMES_IN_FLIGHT; i++) {
            if (g_pd3dDevice->CreateCommandAllocator(D3D12_COMMAND_LIST_TYPE_DIRECT, IID_PPV_ARGS(&g_frameContext[i].CommandAllocator)) != S_OK)
                return false;
        }
        if (g_pd3dDevice->CreateCommandList(0, D3D12_COMMAND_LIST_TYPE_DIRECT, g_frameContext[0].CommandAllocator, NULL, IID_PPV_ARGS(&g_pd3dCommandList)) != S_OK ||
            g_pd3dCommandList->Close() != S_OK)
            return false;

        if (g_pd3dDevice->CreateFence(0, D3D12_FENCE_FLAG_NONE, IID_PPV_ARGS(&g_fence)) != S_OK)
            return false;

        g_fenceEvent = CreateEvent(NULL, FALSE, FALSE, NULL);
        if (g_fenceEvent == NULL)
            return false;

        CreateRenderTarget();
        return true;
    }
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
