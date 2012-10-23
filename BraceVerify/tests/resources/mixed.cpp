#include<iostream>

// This one should have two sets of valid braces
// But will fail due to one being block and the other being egyptian

int main() {

    if (true)
    {
        std::cout << "this is true!" << std::endl;
    }

    return 0;
}
