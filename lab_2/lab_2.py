class Predmet:
    def __init__(self, name, control):
        self.name = name
        self.control = control

class Kafedra:
    def __init__(self, name):
        self.name = name
        self.chitaet = {}
class Student:
    def __init__(self, student_id, name, spec):
        self.id = student_id
        self.name = name
        self.spec = spec
        self.semester = 1
        self.ocenki = {}
        self.history = {}

class Faculty:
    def __init__(self, name):
        self.name = name
        self.specs = []        
        self.kafedry = []     
        self.students = {}   
        self.next_id = 1  
        def get_student(self, student_id):
         if student_id not in self.students:
         # тут я так понял нужен вызов ошибки надо их будет прописать выше 
            return self.students[student_id]

    def find_department(self, predmet_name, spec):
        for kaf in self.kafedry:
            if predmet_name in kaf.chitaet:
                if spec in kaf.chitaet[predmet_name]:
                    return kaf
        return None
#проверка
def create_faculty():
    pass


#это как бы лобби меню
def student_menu(faculty, student_id):
    pass

def main():
    pass

main()