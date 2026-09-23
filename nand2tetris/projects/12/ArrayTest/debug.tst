load,
output-file debug.out,
output-list time%S1.4.1 RAM[8000]%D2.6.1 PC%D2.6.1;
repeat 100 {
  vmstep;
  output;
}
