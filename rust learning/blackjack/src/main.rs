use std::io; //Input
use std::io::{Write};
use rand::seq::SliceRandom; //Shuffle method
use rand::rng;       //Random number generator

#[derive(Clone)]
struct Card
{
    suit: String,
    value: u8,
}

impl Card
{
    fn print_card(&self) -> String
    {
        match self.value{
            1 => format!("Ace of {0}", self.suit),
            10 => format!("Jack of {0}", self.suit),
            11 => format!("Queen of {0}", self.suit),
            12 => format!("King of {0}", self.suit),
            _ => format!("{0} of {1}", self.value, self.suit),

        }
        
    }
}

struct Hand
{
    hand_new: Vec<Card>,
    total: u8,
}

impl Hand
{
    fn new() -> Hand
    {   
        let hand_new = Vec::new();
        let total = 0;

        Hand {hand_new, total}
    }

    fn print_hand(&self)
    {
        for n in &self.hand_new
        {
            println!("{}", n.print_card());
        }
    }

    fn check_ace(&self) -> bool
    {
        for c in &self.hand_new
        {
            if c.value == 1
            {
                return true;
            }
        }
        false
    }

}

struct Deck
{
    deck_new: Vec<Card>,
}

impl Deck
{

    fn new() -> Deck
    {
        let mut deck_new = Vec::new();
        let suits= vec!["Diamonds", "Spades", "Clubs", "Hearts"];

        for s in suits{
            for n in 1..=12{
                deck_new.push(Card{
                    suit: s.to_string(),
                    value: n,
                });

            }
        }
        Deck {deck_new}
    }

    fn shuffle_deck(&mut self)
    {
        self.deck_new.shuffle(&mut rng());
    }
}

struct BlackJack
{
    bj_deck: Deck,
    dealer: Hand,
}

impl BlackJack
{
    fn new() ->BlackJack
    {
        let mut bj_deck = Deck::new();
        let dealer = Hand::new();

        bj_deck.shuffle_deck();

        BlackJack {bj_deck, dealer}
    }
    fn get_dealer_total(&self) -> u8
    {
        self.dealer.total
    }

    fn deal_player(&mut self, passed_hand: &mut Hand)
    {
        if let Some(card) = self.bj_deck.deck_new.pop() {
            passed_hand.hand_new.push(card.clone());
            if card.value==1 && passed_hand.total <= 10
            {
                passed_hand.total += 11;
            }
            else
            {
                passed_hand.total += card.value;
            }
        }
    }
    fn deal_self(&mut self)
    {
        if let Some(card) = self.bj_deck.deck_new.pop() {
            self.dealer.hand_new.push(card.clone());
            self.dealer.total += card.value;
        }
    }
}

fn read_input(prompt: &str) -> String {
    print!("{}", prompt);

    io::stdout().flush().expect("Failed to flush stdout");

    let mut input = String::new();

    io::stdin()
        .read_line(&mut input)
        .expect("Failed to read line");

    input.trim().to_string()
}

fn main() {
    let mut new_game: BlackJack; //use :: for functions not using self, and . for ones that do
    let mut my_hand: Hand;

    let mut play_game;
    let mut game_input: u8;

    let mut temp_input;

    play_game = read_input("Welcome to Camren's Rust BlackJack! Would you like to play? (Y/N):  ");

    while !play_game.eq_ignore_ascii_case("y") && !play_game.eq_ignore_ascii_case("n")
    {
        read_input("Invalid input! Enter Y for yes, or N for no:");
    }

    while play_game.eq_ignore_ascii_case("y")
    {
        println!("\n");
        new_game = BlackJack::new();
        my_hand = Hand::new();

        for _n in 1..3
        {
            new_game.deal_player(&mut my_hand);
            println!("The dealer deals you a card. Its the {}.", my_hand.hand_new.last().unwrap().print_card());
            new_game.deal_self();
        }
        println!("Your total: {}", my_hand.total);
        
        loop
        {
            temp_input = read_input("\nWhat would you like to do? Enter the corresponding number:\n
            1. Look at hand
            2. Hit
            3. Stay
        
            Enter:  ");

            while temp_input!="1".to_string() && temp_input!="2".to_string() && temp_input!="3".to_string()
            {
                temp_input = read_input("\tInvalid input! Select a numerical option 1-3 as shown above: ");
            }

            game_input = temp_input.parse().unwrap();

            match game_input{
                1 => {
                    println!("Your hand:");
                    my_hand.print_hand();
                    println!("Your total: {}", my_hand.total);
                    }
                2 => {
                    new_game.deal_player(&mut my_hand);
                    println!("\nThe dealer deals you a card. Its the {}. \nYour new total is {}.", my_hand.hand_new.last().unwrap().print_card(), my_hand.total);
                    
                    if my_hand.total > 21
                    {
                        if my_hand.check_ace()
                        {
                            my_hand.total -= 10;
                        }

                        else
                        {
                            game_input = 3;
                        }
                    }

                    if my_hand.total == 21
                    {
                        game_input = 3;
                    }
                }
                _=> (),
            }

            if game_input!=1 && game_input!=2
            {
                break;
            }

        }

        
        if my_hand.total > 21
        {
            println!("Bust! Your card total is over 21! You Lose!");
        }

        else if my_hand.total == 21
        {
            println!("You win! Your card total is exactly 21!");
        }

        else
        {
            if my_hand.total > new_game.get_dealer_total()
            {
                println!("You win! Your card total is higher than the dealer.");
            }
            else if my_hand.total == new_game.get_dealer_total()
            {
                println!("You and the dealer tied. You lose!");
            }
            else
            {
                println!("You lose! Your card total is lower than the dealer.");
            }

            println!("You: {}\nDealer: {}", my_hand.total, new_game.get_dealer_total());
        }

        play_game = read_input("Would you like to play again? (Y/N):  ");

        while !play_game.eq_ignore_ascii_case("y") && !play_game.eq_ignore_ascii_case("n")
        {
            read_input("Invalid input! Enter Y for yes, or N for no:");
        }
    }    
}
