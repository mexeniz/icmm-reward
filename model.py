class ICMMRunner:
    GENDER_MALE = 'M'
    GENDER_FEMALE = 'F'

    RACE_10K = '10K'
    RACE_5K = '5K'

    def __init__(self, bib_number,  **kwargs):
        # Validate arguments.
        if int(bib_number) < 0:
            raise ValueError(
                'bib_number should be zero or positive number: {}'.format(bib_number))

        self.bib_number = int(bib_number)
        self.firstname = kwargs.get('firstname', None)
        self.lastname = kwargs.get('lastname', None)
        self.gender = kwargs.get('gender', None)
        self.tel_4_digit = kwargs.get('tel_4_digit', None)
        self.race = kwargs.get('race', None)
        self.full_bib = kwargs.get('full_bib', None)
        self.name_on_bib = kwargs.get('name_on_bib', None)
        self.feedback = kwargs.get('feedback', None)
        self.challenge = kwargs.get('challenge', None)
        self.challenge_result = kwargs.get('challenge_result', None)

    def to_doc(self):
        doc = {
            'bibNumber': self.bib_number,
            'firstname': self.firstname,
            'lastname': self.lastname,
            'race': self.race,
            'gender': self.gender,
            'tel4Digit': self.tel_4_digit,
            'fullBib': self.full_bib,
            'nameOnBib': self.name_on_bib,
            'feedback': self.feedback,
            'challenge': self.challenge,
            'challengeResult': self.challenge_result
        }
        return doc

    def __str__(self):
        return str(self.to_doc())

    @classmethod
    def from_doc(cls, doc):
        bib_number = doc.get('bibNumber', None)
        firstname = doc.get('firstname', None)
        lastname = doc.get('lastname', None)
        race = doc.get('race', None)
        gender = doc.get('gender', None)
        tel_4_digit = doc.get('tel4Digit', None)
        full_bib = doc.get('fullBib', None)
        name_on_bib = doc.get('nameOnBib', None)
        feedback = doc.get('feedback', None)
        challenge = doc.get('challenge', None)
        challenge_result = doc.get('challengeResult', None)
        return cls(bib_number, 
            firstname=firstname,  
            lastname=lastname, 
            gender=gender,
            tel_4_digit=tel_4_digit,
            race=race,
            full_bib=full_bib,
            name_on_bib=name_on_bib,
            feedback=feedback,
            challenge=challenge,
            challenge_result=challenge_result
            )