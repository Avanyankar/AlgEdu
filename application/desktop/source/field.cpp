#include <vector>

class Cell
{
public:
    int x;
    int y;
};

class Field
{
public:
    std::vector<std::vector<Cell>> cells;

    Field(int w = 0, int h = 0) : cells(h, std::vector<Cell>(w))
    {
        for (int y = 0; y < h; y++)
            for (int x = 0; x < w; x++)
                cells[y][x] = { x, y };
    }

    ~Field()
    {

    }

    Cell& at(int x, int y)
    {
        return cells[y][x];
    }
};
