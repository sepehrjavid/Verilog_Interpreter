# Verilog_Interpreter
A simple verilog interpreter that covers simple hardware description like wire, logical operators, truth table, etc

To run the interpreter:

```
python3 project.py
```

Then you will be asked to provide the filename in which your verilog code exists:

```
Please Enter File Name:sep.txt
```

Second, you need to enter the filename in which your test values and delays are:

```
Please Enter The Required File To Draw The Chart:draw.txt
```

Finally, the program asks you to enter the name of the wire of which you want to see the logical behaviour

```
Please Enter The Node You Want To Track: mid1
```

After you're done with the chart, simply click on the window to close.
note that the logical behaviour takes the gate delay into account.
you can also see the summary of your design in the generated file named 'result.data'.
