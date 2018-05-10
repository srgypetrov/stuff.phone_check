extern crate csv;
extern crate sha1;
extern crate rayon;

use std::collections::HashSet;
use std::env::args;
use std::error::Error;
use std::fs::File;
use std::process;
use std::time::Instant;

use csv::ReaderBuilder;
use rayon::prelude::*;


const FILES: [&str; 4] = [
    "DEF-9x.csv",
    "ABC-8x.csv",
    "ABC-3x.csv",
    "ABC-4x.csv"
];
type Record = (u16, u32, u32, u32, String, String);


fn get_wanted_hashes() -> Result<HashSet<String>, String> {
    let wanted_hashes: HashSet<String> = args().skip(1).collect();
    if wanted_hashes.is_empty() {
        return Err(From::from("Expected hashes, got none"))
    }
    Ok(wanted_hashes)
}


fn check_hashes(record: Record, wanted: &HashSet<String>) -> HashSet<String> {
    let (code, start, end, ..) = record;
    (start..end + 1).into_par_iter().filter_map(|number| {
        let phone_number = format!("7{}{:07}", code, number);
        let phone_hash = sha1::Sha1::from(&phone_number).digest().to_string();
        if wanted.contains(&phone_hash) {
            println!("PHONE:{} {}", phone_number, phone_hash);
            return Some(phone_hash)
        }
        return None
    }).collect()
}


fn scan_file(
    fileno: usize,
    filename: &str,
    wanted: &HashSet<String>,
    found: &mut HashSet<String>
) -> Result<bool, Box<Error>> {
    let base_dir = std::env::current_dir()?;
    let file = File::open(base_dir.join("registry").join(&filename))?;
    let mut rdr = ReaderBuilder::new().flexible(true).delimiter(b';').from_reader(file);
    for (i, result) in rdr.deserialize().enumerate() {
        if i % 1000 == 0 {
            println!("LINE:{} {} {}", fileno, filename, i);
        }
        let record: Record = result?;
        let checked_hashes = check_hashes(record, &wanted);
        found.extend(checked_hashes);
        if found.is_superset(&wanted) {
            return Ok(true)
        }
    }
    return Ok(false)
}


fn run() -> Result<(), Box<Error>> {
    let wanted_hashes = get_wanted_hashes()?;
    let mut found_hashes: HashSet<String> = HashSet::new();
    for (fileno, filename) in FILES.iter().enumerate() {
        if scan_file(fileno + 1, filename, &wanted_hashes, &mut found_hashes)? {
            return Ok(())
        }
    }
    for phone in wanted_hashes.difference(&found_hashes) {
        println!("UNKNOWN:{}", phone);
    }
    Ok(())
}


fn main() {
    let start = Instant::now();
    if let Err(err) = run() {
        println!("ERROR:{}", err);
        process::exit(1);
    }
    println!("RUNTIME:{}", start.elapsed().as_secs());
}
