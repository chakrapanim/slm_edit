"""
Synthetic dataset generator for grammar correction evaluation
Creates test cases for typos, grammatical errors, and rephrasing
"""

import pandas as pd
import random

class DatasetGenerator:
    def __init__(self):
        self.typo_examples = []
        self.grammar_examples = []
        self.rephrasing_examples = []
    
    def generate_typo_dataset(self):
        """Generate test cases for typos and misspellings"""
        typo_cases = [
            # Common typos
            ("I recieved your email yesterday.", "I received your email yesterday."),
            ("The weather is beautifull today.", "The weather is beautiful today."),
            ("Please seperate the items.", "Please separate the items."),
            ("I definately agree with you.", "I definitely agree with you."),
            ("The accomodation was excellent.", "The accommodation was excellent."),
            ("We need to analize the data.", "We need to analyze the data."),
            ("This is a common occurance.", "This is a common occurrence."),
            ("The document was mispelled.", "The document was misspelled."),
            ("She was embarassed by the mistake.", "She was embarrassed by the mistake."),
            ("The calender is on the wall.", "The calendar is on the wall."),
            
            # Word confusion
            ("Their going to the store.", "They're going to the store."),
            ("Your welcome to join us.", "You're welcome to join us."),
            ("Its a beautiful day.", "It's a beautiful day."),
            ("The affect of the change was positive.", "The effect of the change was positive."),
            ("I except your invitation.", "I accept your invitation."),
            ("The principle of the school spoke.", "The principal of the school spoke."),
            ("I loose my keys often.", "I lose my keys often."),
            ("The dessert was delicious.", "The desert was hot."),  # Context dependent
            ("I need advise on this matter.", "I need advice on this matter."),
            ("The weather will effect our plans.", "The weather will affect our plans."),
            
            # Missing letters
            ("I wil be there soon.", "I will be there soon."),
            ("Ths is important.", "This is important."),
            ("We shoud consider this option.", "We should consider this option."),
            ("The resut was unexpected.", "The result was unexpected."),
            ("Pleas send the document.", "Please send the document."),
            
            # Extra letters
            ("I recieeved the package.", "I received the package."),
            ("The committe will meet tomorrow.", "The committee will meet tomorrow."),
            ("She was embarassed by the error.", "She was embarrassed by the error."),
            ("The accomodation was nice.", "The accommodation was nice."),
            ("We need to analize the results.", "We need to analyze the results."),
            
            # Transposed letters
            ("The tehcnician fixed the issue.", "The technician fixed the issue."),
            ("I recieved your message.", "I received your message."),
            ("The calender shows the date.", "The calendar shows the date."),
            ("She was embarassed.", "She was embarrassed."),
            ("The accomodation was good.", "The accommodation was good."),
            
            # Common misspellings
            ("The buisness meeting is at 3pm.", "The business meeting is at 3pm."),
            ("I apreciate your help.", "I appreciate your help."),
            ("The enviroment is important.", "The environment is important."),
            ("We need to maintan the system.", "We need to maintain the system."),
            ("The goverment announced new policies.", "The government announced new policies."),
            ("I recomend this book.", "I recommend this book."),
            ("The seperate rooms are available.", "The separate rooms are available."),
            ("She was embarassed by the comment.", "She was embarrassed by the comment."),
            ("The calender event is scheduled.", "The calendar event is scheduled."),
            ("We need to analize the situation.", "We need to analyze the situation."),
        ]
        
        self.typo_examples = typo_cases
        return typo_cases
    
    def generate_grammar_dataset(self):
        """Generate test cases for grammatical errors"""
        grammar_cases = [
            # Subject-verb agreement
            ("The team are working hard.", "The team is working hard."),
            ("The students was studying.", "The students were studying."),
            ("Each of the employees have a desk.", "Each of the employees has a desk."),
            ("The data are incorrect.", "The data is incorrect."),
            ("Neither of the options are suitable.", "Neither of the options is suitable."),
            
            # Verb tense
            ("Yesterday I go to the store.", "Yesterday I went to the store."),
            ("I have saw that movie before.", "I have seen that movie before."),
            ("She has wrote the report.", "She has written the report."),
            ("They was waiting for the bus.", "They were waiting for the bus."),
            ("I had went there last week.", "I had gone there last week."),
            
            # Articles
            ("I need a advice.", "I need advice."),
            ("She is an university student.", "She is a university student."),
            ("The honesty is important.", "Honesty is important."),
            ("I saw the elephant at zoo.", "I saw an elephant at the zoo."),
            ("He is the best student in class.", "He is the best student in the class."),
            
            # Prepositions
            ("I am interested on this topic.", "I am interested in this topic."),
            ("The book is different than I expected.", "The book is different from what I expected."),
            ("She arrived to the airport.", "She arrived at the airport."),
            ("I agree with you in this point.", "I agree with you on this point."),
            ("The meeting is in Monday.", "The meeting is on Monday."),
            
            # Punctuation
            ("Its a beautiful day,isnt it?", "It's a beautiful day, isn't it?"),
            ("I like apples, oranges, and bananas.", "I like apples, oranges, and bananas."),
            ("She said,Hello,how are you?", "She said, \"Hello, how are you?\""),
            ("The meeting is at 3pm we should be ready.", "The meeting is at 3pm; we should be ready."),
            ("I went to the store, and bought some milk.", "I went to the store and bought some milk."),
            
            # Sentence fragments
            ("Because I was late.", "I was late."),
            ("Running in the park.", "I was running in the park."),
            ("The book that I read.", "I read the book."),
            ("After finishing the work.", "After finishing the work, I went home."),
            ("While waiting for the bus.", "While waiting for the bus, I read a book."),
            
            # Run-on sentences
            ("I went to the store I bought some milk.", "I went to the store and bought some milk."),
            ("She is smart she works hard.", "She is smart, and she works hard."),
            ("The weather is nice we should go outside.", "The weather is nice; we should go outside."),
            ("I like coffee he prefers tea.", "I like coffee, but he prefers tea."),
            ("It was raining we stayed inside.", "It was raining, so we stayed inside."),
            
            # Double negatives
            ("I don't have no time.", "I don't have any time."),
            ("She can't hardly wait.", "She can hardly wait."),
            ("I didn't see nothing.", "I didn't see anything."),
            ("We don't need no help.", "We don't need any help."),
            ("There isn't no reason to worry.", "There isn't any reason to worry."),
            
            # Pronoun errors
            ("Me and John went to the store.", "John and I went to the store."),
            ("Between you and I, this is wrong.", "Between you and me, this is wrong."),
            ("The teacher gave the assignment to John and I.", "The teacher gave the assignment to John and me."),
            ("Him and me are friends.", "He and I are friends."),
            ("She gave it to he and I.", "She gave it to him and me."),
            
            # Comparative and superlative
            ("This is more better than that.", "This is better than that."),
            ("She is the most smartest student.", "She is the smartest student."),
            ("This is more easier.", "This is easier."),
            ("He is more tall than me.", "He is taller than me."),
            ("The most biggest problem is cost.", "The biggest problem is cost."),
            
            # Conditional sentences
            ("If I was you, I would go.", "If I were you, I would go."),
            ("If he would have known, he would come.", "If he had known, he would have come."),
            ("I wish I was there.", "I wish I were there."),
            ("If it was possible, I would help.", "If it were possible, I would help."),
            ("If I would have time, I would do it.", "If I had time, I would do it."),
        ]
        
        self.grammar_examples = grammar_cases
        return grammar_cases
    
    def generate_rephrasing_dataset(self):
        """Generate test cases for rephrasing to improve clarity and readability"""
        rephrasing_cases = [
            # Wordy phrases
            ("Due to the fact that it was raining, we stayed home.", "Because it was raining, we stayed home."),
            ("In order to complete the task, we need more time.", "To complete the task, we need more time."),
            ("At this point in time, we are ready.", "Now, we are ready."),
            ("For the purpose of saving money, we canceled the trip.", "To save money, we canceled the trip."),
            ("In the event that it rains, bring an umbrella.", "If it rains, bring an umbrella."),
            
            # Passive to active voice
            ("The report was written by John.", "John wrote the report."),
            ("The decision was made by the committee.", "The committee made the decision."),
            ("The car was driven by Sarah.", "Sarah drove the car."),
            ("The meeting was attended by all members.", "All members attended the meeting."),
            ("The problem was solved by the team.", "The team solved the problem."),
            
            # Clarity improvements
            ("The thing that I want to say is that we need to work harder.", "We need to work harder."),
            ("It is important to note that the results are significant.", "The results are significant."),
            ("There are many people who believe this.", "Many people believe this."),
            ("The reason why I came is because I wanted to help.", "I came because I wanted to help."),
            ("The fact of the matter is that we need to change.", "We need to change."),
            
            # Sentence structure
            ("The book, which was written by a famous author, is very popular.", "The book by a famous author is very popular."),
            ("She is a person who is very kind.", "She is very kind."),
            ("The company, which is located in New York, is expanding.", "The New York-based company is expanding."),
            ("The student, who was studying hard, passed the exam.", "The hardworking student passed the exam."),
            ("The project, which was completed on time, was successful.", "The project completed on time was successful."),
            
            # Redundancy
            ("The final outcome was positive.", "The outcome was positive."),
            ("We need to plan ahead for the future.", "We need to plan for the future."),
            ("The end result was satisfactory.", "The result was satisfactory."),
            ("We need to collaborate together.", "We need to collaborate."),
            ("The past history shows a pattern.", "The history shows a pattern."),
            
            # Awkward phrasing
            ("I would like to make a request for more information.", "I would like more information."),
            ("We are in the process of reviewing the documents.", "We are reviewing the documents."),
            ("I am of the opinion that this is correct.", "I think this is correct."),
            ("We need to have a discussion about this.", "We need to discuss this."),
            ("She has the ability to solve problems.", "She can solve problems."),
            
            # Flow and readability
            ("The meeting was long. It was also boring.", "The meeting was long and boring."),
            ("He is smart. He is also hardworking.", "He is smart and hardworking."),
            ("The weather is nice. We should go outside.", "Since the weather is nice, we should go outside."),
            ("I was tired. I still finished the work.", "Although I was tired, I still finished the work."),
            ("She studied hard. She passed the exam.", "She studied hard, so she passed the exam."),
            
            # Conciseness
            ("The company is in the process of expanding its operations.", "The company is expanding its operations."),
            ("We are currently working on the project.", "We are working on the project."),
            ("I would like to take this opportunity to thank you.", "Thank you."),
            ("It is my belief that we should proceed.", "I believe we should proceed."),
            ("We are experiencing a situation where delays occur.", "We are experiencing delays."),
            
            # Better word choice
            ("The utilization of resources is important.", "Using resources efficiently is important."),
            ("We need to facilitate the process.", "We need to make the process easier."),
            ("The implementation of the plan was successful.", "The plan was successfully implemented."),
            ("We need to optimize our performance.", "We need to improve our performance."),
            ("The demonstration of skills was impressive.", "The skills demonstrated were impressive."),
        ]
        
        self.rephrasing_examples = rephrasing_cases
        return rephrasing_cases
    
    def generate_all_datasets(self):
        """Generate all test datasets"""
        print("Generating typo test cases...")
        typo_data = self.generate_typo_dataset()
        
        print("Generating grammar test cases...")
        grammar_data = self.generate_grammar_dataset()
        
        print("Generating rephrasing test cases...")
        rephrasing_data = self.generate_rephrasing_dataset()
        
        return typo_data, grammar_data, rephrasing_data
    
    def save_to_csv(self, filename="test_dataset.csv"):
        """Save all datasets to a CSV file"""
        typo_data, grammar_data, rephrasing_data = self.generate_all_datasets()
        
        # Combine all data
        all_data = []
        
        for incorrect, correct in typo_data:
            all_data.append({
                "Category": "Typo",
                "Input_Text": incorrect,
                "Ground_Truth": correct
            })
        
        for incorrect, correct in grammar_data:
            all_data.append({
                "Category": "Grammar",
                "Input_Text": incorrect,
                "Ground_Truth": correct
            })
        
        for incorrect, correct in rephrasing_data:
            all_data.append({
                "Category": "Rephrasing",
                "Input_Text": incorrect,
                "Ground_Truth": correct
            })
        
        # Create DataFrame and save
        df = pd.DataFrame(all_data)
        df.to_csv(filename, index=False)
        print(f"Dataset saved to {filename}")
        print(f"Total test cases: {len(df)}")
        print(f"  - Typos: {len(typo_data)}")
        print(f"  - Grammar: {len(grammar_data)}")
        print(f"  - Rephrasing: {len(rephrasing_data)}")
        
        return df

if __name__ == "__main__":
    generator = DatasetGenerator()
    df = generator.save_to_csv("test_dataset.csv")
