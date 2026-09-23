load,
output-file trace.out,
output-list RAM[0]%D2.6.1 RAM[8000]%D2.6.1;
repeat 3000000 {
  vmstep;
}
output;
