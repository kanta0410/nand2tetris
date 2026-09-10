// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/4/Fill.asm

// Runs an infinite loop that listens to the keyboard input. 
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel. When no key is pressed, 
// the screen should be cleared.

//Main
(LOOP)
    @KBD
    D=M
    
    @BLACK
    D;JNE

    @WHITE
    0;JMP

    

(BLACK)
    @color
    M=-1

    @PAINT
    0;JMP

(WHITE)
    @color
    M=0

    @PAINT
    0;JMP

(PAINT)
    @SCREEN
    D=A

    @address
    M=D

(PIXEL_LOOP)
    @color
    D=M

    @address
    A=M
    M=D

    @address
    M=M+1
    
    @address
    D=M

    @KBD
    D=D-A

    @PIXEL_LOOP
    D;JLT

    @LOOP
    0;JMP


