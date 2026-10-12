use std::io;

fn func_select(selection: i32)
{
    if selection == 1 {add();}
    else if selection == 2 {subtract();}
    else if selection == 3 {multiply();}
    else if selection == 4 {divide();}
    else {println!("Function {} does not exist. Try again.", selection);}
}

fn read_num(prompt: &str) -> f64
{
    let mut input = String::new(); //input is always a string
    println!("{}", prompt);
    io::stdin().read_line(&mut input).expect("Failed to read line");
    input.trim().parse().expect("invalid input")
}

fn enter_num() -> (f64, f64)
{
   (read_num("Enter number 1:"), read_num("Enter number 2:"))
}

fn add()
{
    let (num1, num2) = enter_num();
    println!("\n{}+{}={}\n", num1, num2, num1 + num2);
}

fn subtract()
{
    let (num1, num2) = enter_num();
    println!("\n{}-{}={}\n", num1, num2, num1 - num2);
}

fn multiply()
{
    let (num1, num2) = enter_num();
    println!("\n{}*{}={}\n", num1, num2, num1 * num2);
}

fn divide()
{
    let (num1, num2) = enter_num();
    println!("\n{}/{}={}\n", num1, num2, num1 / num2);
}




fn main() {
    let mut input = String::new();

    println!("Welcome to the calculator program!\n");

    loop
    {
        println!("Select from the operations below (enter the number associated):");
        println!("Add: 1");
        println!("Subtract: 2");
        println!("Multiply: 3");
        println!("Divide: 4");
        println!("Exit: 0\n");
        println!("Enter here: ");

        let _ = io::stdin().read_line(&mut input).expect("Failed to read line");
        let selection: i32 = input.trim().parse().expect("invalid input");
        input.clear(); //clears out the input for the next loop

        if selection == 0
        {
            break;
        }

        else
        {
            func_select(selection);
        }

    }
}
