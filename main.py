class Exersise:
    def __init__(self,name, duration, intensity):
        self.name = name
        self.duration = duration
        self.intensity = intensity

class User:
    def __init__(self,username):
        self.username = (username)
        self.exersises = []
        self.goals = []

    def log_exersise(self, exersise):
        self.exersises.append(exersise)

    def calculate_calories_burned(self):
        total_calories = 0
        for exersise in self.exersises:
           calories = exersise.duration * exersise.intensity
           total_calories += calories
        return total_calories
    
    def set_goals(self, goal, target_reps):
        self.goals[goal] = target_reps  

    def track_progress(self):
        
        total_calories = self.calculate_calories_burned()
        if'calories' in self.goals:
            goal_calories = self.goals['calories']
            progress_precentage = (total_calories / goal_calories) * 100
            return f"Progress towards calorie goal: {progress_precentage}%"
        else: 
            return "No calorie goal set."

def log_exersise(user):
    name = input("Exerise name: ")
    duration = int(input("Duration (in minutes): "))
    intensity = int(input("Intensity (1-10): "))
    exersise = Exersise(name, duration, intensity)
    user.log_exersise(exersise)
    print(f"Exersise '{name}' logged successfully!")

def set_goals(user):
    goal_type = input("Set a goal (eg 'calories', 'reps'): ")
    target_value = int(input("Target value: "))
    user.set_goals(goal_type, target_value)
    print("goal set successfully!")

def track_progress(user):
    progress = user.track_progress()
    if progress is not None:
        print(f"progress towards goal: {progress:.2f}")
    else: 
        print("No progress to track.")
        
def main():
    username = input("Enter your username: ")
    user = User(username)
    
    while True:
        print("\n1. Log Exersise")
        print("2. Set Goals")
        print("3. Track Progress")
        print("4. Exit")
        
        choice = input("Choose an option: ")
        
        if choice == '1':
            log_exersise(user)
        elif choice == '2':
            set_goals(user)
        elif choice == '3':
            track_progress(user)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
#code creates a fintniss tracker in the console really basic but it works. 
       
       