import subprocess

verilog_txt = """
`timescale 1ns / 1ns

module start_tb_two;

    // Inputs
    reg request1 = 0;
    reg request2 = 0;
    reg request3 = 0;
    reg reset = 1;
    reg clk = 1;

    // Outputs
    wire grant1, grant2, grant3;

    // Instantiate the arbiter module
    start uut (
        .request1(request1),
        .request2(request2),
        .request3(request3),
        .clk(clk),
        .reset(reset),
        .grant1(grant1),
        .grant2(grant2),
        .grant3(grant3)
    );

    // Clock generation
    always begin
        #5 clk = ~clk;
    end

    // Initial reset
    initial begin
        reset = 1;
        #10 reset = 0;
    end

    // Test scenario
    initial begin
        
        $dumpfile("start_tb_two.vcd");
        $dumpvars(0, start_tb_two);
        request1 = 0;
        request2 = 0;
        request3 = 0;

        // Test case 1: request1 is active
        #15 request1 = 1;
        #50 request1 = 0;

        // Test case 2: request2 is active
        #15 request2 = 1;
        #50 request2 = 0;

        // Test case 3: request3 is active
        #15 request3 = 1;
        #50 request3 = 0;

        // Test case 4: multiple requests are active
        #15 request1 = 1;
        #5 request2 = 1;
        #5 request3 = 1;
        #50 request1 = 0;
        #50 request2 = 0;
        #50 request3 = 0;

        // Add more test cases as needed

        // End simulation
        #10 $finish;
    end

endmodule
"""

#f = open("start_tb_two.v", 'w')
#f.write(verilog_txt)
#f.close()

def run_verilog_testbench():
    compile_cmd = ["iverilog", "-o", "FIFO_tb.vvp", "FIFO.v", "FIFO_tb.v"]
    compile_process = subprocess.run(compile_cmd, capture_output=True, text=True)
    if compile_process.returncode != 0:
        print("Compilation Error:")
        print(compile_process.stderr)
        return ['err', compile_process.stderr]
    run_cmd = ["vvp", "FIFO_tb.vvp"]
    run_process = subprocess.run(run_cmd, capture_output=True, text=True)
    if run_process.returncode != 0:
        print("Runtime Error:")
        print(run_process.stderr)
        return ['err', run_process.stderr]

    # Print the output
    print("Testbench Output:")
    print(run_process.stdout)
    #compile total time passed until error
    #find current value of each variable
    f = open('FIFO_tb.vcd', 'r')
    lines = "".join(f.readlines())
    vars = lines.split("$scope module FIFO_tb $end")[1]
    vars_tb = vars.split("$scope module fifo_inst $end")[0]
    vars_tb = vars_tb.split("\n")
    vars_tb.pop(0)
    vars_tb.pop(-1)
    vars_mod = vars.split("$scope module fifo_inst $end")[1]
    vars_mod = vars_mod.split("$upscope $end")[0]
    vars_mod = vars_mod.split("\n")
    vars_mod.pop(0)
    vars_mod.pop(-1)
    vars_tb_dict = {}
    tb_sym_to_var = {}
    for var in vars_tb:
        print(var.split(" "))
        vars_tb_dict[var.split(" ")[4]] = var.split()[3]
        tb_sym_to_var[var.split(" ")[3]] = var.split()[4]
    for var in vars_mod:
        if var.split(" ")[4] not in vars_tb_dict.keys():
            vars_tb_dict[var.split(" ")[4]] = var.split()[3]
        tb_sym_to_var[var.split(" ")[3]] = var.split()[4]
    print(vars_tb_dict)
    var_lst = []
    val_lst = []
    for key in tb_sym_to_var.keys():
        var_lst.append(key)
        val_lst.append([])
    vals = lines.split("$dumpvars")[1]
    vals_lst = vals.split("\n")
    vals_lst.pop(0)
    vals_lst.pop(-1)
    counter = 0
    for line in vals_lst:
        if line[0] != "#":
            line_lst = line.split(" ")
            if len(line_lst) > 1:
                val = line_lst[0]
                val = val[1:]
                val = val[::-1]
                num = 0
                for i, char in enumerate(val):
                    if char.isnumeric():
                        num += int(char)*(2**i)
                    else:
                        num = 'x'
                        break
                if line_lst[1] in var_lst:
                    val_lst[var_lst.index(line_lst[1])].append(num)
        else:
            line = line[1:]
            counter += int(line)
        wrong = vars_tb_dict['incorrect_values']
        if val_lst[var_lst.index(wrong)] == "1":
            return ["err", str("Incorrect value read at "+str(counter)+" ticks")]
    return ["final"]
result = run_verilog_testbench()
print(result)
print('v')
