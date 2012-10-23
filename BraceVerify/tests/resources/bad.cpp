#include<iostream>

// This one should fail with none of the three passing

int main() {

    if (true)
    {
        std::cout << "this is true!" << std::endl; }

    if (false) {
        std::cout << "this will never print" << std::endl;
     }

    return 0; }
