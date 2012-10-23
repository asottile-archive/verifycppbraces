#include<iostream>

// This one should pass even though there are braces in a character.

int main()
{

    if (true)
    {
        std::cout << "this is true !" << '{' << std::endl;
    }

    return 0;
}
