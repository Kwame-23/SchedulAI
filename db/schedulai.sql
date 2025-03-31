---------

CREATE DATABASE schedulai;
USE schedulai;

CREATE TABLE Roles (
    RoleID INT PRIMARY KEY AUTO_INCREMENT,
    RoleName VARCHAR(50) UNIQUE NOT NULL
);

INSERT INTO Roles (RoleName) VALUES ('Admin');
INSERT INTO Roles (RoleName) VALUES ('User');

CREATE TABLE Users (
    UserID INT PRIMARY KEY AUTO_INCREMENT,
    Username VARCHAR(50) UNIQUE NOT NULL,
    Email VARCHAR(100) UNIQUE NOT NULL,
    PasswordHash VARCHAR(255) NOT NULL, -- Store hashed passwords, not plain text
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    RoleID INT NOT NULL, -- Foreign key to Roles table
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UpdatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (RoleID) REFERENCES Roles(RoleID)
);


CREATE TABLE UserSessions (
    SessionID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    SessionToken VARCHAR(255) NOT NULL,
    ExpiresAt TIMESTAMP NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE PasswordResets (
    ResetID INT PRIMARY KEY AUTO_INCREMENT,
    UserID INT NOT NULL,
    ResetToken VARCHAR(255) NOT NULL,
    ExpiresAt TIMESTAMP NOT NULL,
    CreatedAt TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE SessionType (
    SessionTypeID INT PRIMARY KEY AUTO_INCREMENT,
    SessionTypeName VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO SessionType (SessionTypeID, SessionTypeName)
VALUES
(1, 'Discussion'),
(2, 'Independent Study'),
(3, 'Lab'),
(4, 'Lecture'),
(5, 'Period'),
(6, 'Seminar'),
(7, 'Set up for grading only');

CREATE TABLE Room (
    RoomID INT PRIMARY KEY AUTO_INCREMENT,
    Location VARCHAR(255) NOT NULL UNIQUE,
    MaxRoomCapacity INT NOT NULL
) ENGINE=InnoDB;

INSERT INTO Room (RoomID, Location, MaxRoomCapacity) 
VALUES
(1, 'Apt Hall 216', 74),
(2, 'Apt Hall 217', 75),
(3, 'Bio Lab', 33),
(4, 'D-Lab 102', 58),
(5, 'Databank Foundation Hall 218', 75),
(6, 'EE lab', 52),
(7, 'Fab Lab 103', 31),
(8, 'Fab Lab 203', 72),
(9, 'Fab Lab 303', 75),
(10, 'Jackson Hall 115', 76),
(11, 'Jackson Hall 116', 79),
(12, 'Jackson Lab 221', 59),
(13, 'Jackson Lab 222', 61),
(14, 'Norton-Motulsky 207A', 58),
(15, 'Norton-Motulsky 207B', 69),
(16, 'Nutor Hall 100', 100),
(17, 'Nutor Hall 115', 73),
(18, 'Nutor Hall 216', 68),
(19, 'Radichel MPR', 55),
(20, 'Science Lab', 47);

CREATE TABLE FacultyType (
    FacultyTypeID INT PRIMARY KEY AUTO_INCREMENT,
    FacultyTypeName VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO FacultyType (FacultyTypeID, FacultyTypeName)
VALUES
(1, 'Lecturer'),
(2, 'Adjunct Faculty'),
(3, 'Faculty Intern');

CREATE TABLE Lecturer (
    LecturerID INT PRIMARY KEY AUTO_INCREMENT,
    LecturerName VARCHAR(255) NOT NULL,
    FacultyTypeID INT NOT NULL,
    FOREIGN KEY (FacultyTypeID) REFERENCES FacultyType(FacultyTypeID)
) ENGINE=InnoDB;



-- Populate Lecturer table with extracted lecturer names
INSERT IGNORE INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
(1, 'Acheampong Antwi Afari', 1),
(2, 'Afiah Agyeman Amponsah-Mensah', 1),
(3, 'Albert Agyepong', 1),
(4, 'Albert Cofie', 1),
(5, 'Alhassan Sullaiman', 1),
(6, 'Anthony Essel-Anderson', 1),
(7, 'Anthony Spio', 1),
(8, 'Awingot Richard Akparibo', 1),
(9, 'Ayawoa Dagbovie', 1),
(10, 'Ayorkor Korsah', 1),
(11, 'Baah Aye Kusi', 1),
(12, 'Bright Tetteh', 1),
(13, 'Charles Adjetey', 1),
(14, 'Christine Onyinah', 1),
(15, 'David Amatey Sampah', 1),
(16, 'David Ebo Adjepon-Yamoah', 1),
(17, 'Dennis Owusu Asamoah', 1),
(18, 'Dionne Boateng', 1),
(19, 'Dirk Kleine', 1),
(20, 'Disraeli Asante-Darko', 1),
(21, 'Ebenezer Obiri Addo', 1),
(22, 'Edgar Francis Cooke', 1),
(23, 'Elena Victoria Rosca', 1),
(24, 'Enock Opoku', 1),
(25, 'Enyonam Kudonoo', 1),
(26, 'Eric Ocran', 1),
(27, 'George Francois', 1),
(28, 'Gideon Osabutey', 1),
(29, 'Godwin Ayetor', 1),
(30, 'Govindha Ramaiah Yeluripati', 1),
(31, 'Hassan Wahab', 1),
(32, 'Hyder Ali Segu Mohamed', 1),
(33, 'Isaac Nyantakyi', 1),
(34, 'Ishmael Asiedu', 1),
(35, 'Jamal-Deen Abdulai', 1),
(36, 'Joseph Adjei', 1),
(37, 'Joseph Mensah', 1),
(38, 'Joseph Oduro-Frimpong', 1),
(39, 'Josephine Djan', 1),
(40, 'Justice Kwame Appati', 1),
(41, 'Kobby Amoah', 1),
(42, 'Kofi Adu-Labi', 1),
(43, 'Kwaku Asante', 1),
(44, 'Kweku Dwomoh', 1),
(45, 'Maame Mensa-Bonsu', 1),
(46, 'Maame Yaa Mensa-Bonsu', 1),
(47, 'Michael Effah Asamoah', 1),
(48, 'Millicent Awuku', 1),
(49, 'Miriam Abade-Abugre', 1),
(50, 'Naa Adjeley Doamekpor', 1),
(51, 'Nana Kwasi Karikari', 1),
(52, 'Nathan Nyarko Amanquah', 1),
(53, 'Nii Tettey', 1),
(54, 'Patrick Dwomfuor', 1),
(55, 'Prince Acquaye', 1),
(56, 'Prince Baah', 1),
(57, 'Robert Sowah', 1),
(58, 'Saeed Moomin', 1),
(59, 'Sampson Dankyi Asare', 1),
(60, 'Shefi Nelson', 1),
(61, 'Sihaam Mohammed Sayuti', 1),
(62, 'Stephen Emmanuel Armah', 1),
(63, 'Stephen K. Armah', 1),
(64, 'Sussan Einakian', 1),
(65, 'Theodora Aryee', 1),
(66, 'Umut Tosun', 1),
(67, 'Prince Tetteh', 3),
(68, 'Emmanuel Darko', 3),
(69, 'Gabriel Oboamah Affum', 3),
(70, 'Yayra Azaglo', 3),
(71, 'Evans Ghansah', 3),
(72, 'Christelle Afua Asantewaa McCarthy', 3),
(73, 'Owuraku Obeng Osei-Dwammena', 3),
(74, 'Akosua Obeng', 3),
(75, 'Dominic Ayiquaye', 3),
(76, 'Mary Magdalene Eliason', 3),
(77, 'Francis Eduku', 1),
(78, 'Freda Dzradosi', 2),
(79, 'Jewel Thompson', 1),
(80, 'Esther Afoley Laryea', 1),
(81, 'Gordon Kwesi Adomdza', 1),
(82, 'Keren Arthur', 2),
(83, 'Samuel Darko', 1),
(84, 'Joel Bortey', 3),
(85, 'Kwabena Ampadu Bamfo', 1),
(86, 'Stephane Nwolley', 2),
(87, 'Heather Beem', 1),
(88, 'Adwoa Yirenkyi-Fianko', 2),
(89, 'Yaw Delali Bensah', 2),
(90, 'Aminu Shittu', 2),
(91, 'University of Toronto Faculty', 2),
(92, 'Annajiat Alim Rasel', 2),
(93, 'Natalie Fordwor', 2),
(94, 'Gideon Hosu-Porbley', 2),
(95, 'Alimsiwen Ayaawan', 1),
(96, 'Michael Osei', 3),
(97, 'Brian Botchway', 3),
(98, 'Katelyn Aba Dadzie', 3),
(99, 'Noelle Naa Kai Kotei', 3),
(100, 'Nana Yaa Annorbea Frempong', 3),
(101, 'Richard Ekumah', 3),
(102, 'Knowledge Ahadzitse', 3),
(103, 'Rosemary Abowine', 3),
(104, 'Elaine Eyram Roberts', 3),
(105, 'David Asiamah Boateng', 3),
(106, 'Ewura Abena Asmah', 3),
(107, 'Karen Effiba Blay', 3),
(108, 'Emmanuel Affoh', 3),
(109, 'Benjamin Kofi Ampomah Nkansah', 3),
(110, 'Nana Adjoa Aseye Senanu', 3),
(111, 'Anna Naami', 3),
(112, 'Albert Akatom Bensusan', 1),
(113, 'Prince Aning', 1),
(114, 'Rebecca Awuah', 1),
(115, 'Linda Arthur', 3),
(116, 'Percy Brown', 3),
(117, 'Felicity Kuwornoo', 3),
(118, 'Faith Timoh', 3),
(119, 'Dickson Akubia', 3),
(120, 'Nana Banyin Ayeyi Djan', 3),
(121, 'Nanna Abankwa', 3),
(122, 'Samantha Mavunga', 3),
(123, 'Kasim Ibrahim', 3),
(124, 'Silas Sangmin', 3),
(125, 'Abdul-Aziz Fuseini', 3),
(126, 'Elijah Kwaku Adutwum Boateng', 3),
(127, 'Akwasi Asante-Krobea', 3),
(128, 'Gideon Donkor Bonsu', 3),
(129, 'Kweku Yamoah', 3),
(130, 'Nana Adwoa Newman', 3),
(131, 'Kwadwo Ansong Annor', 3),
(132, 'Jesse Korku Seyram Agbenya', 3),
(133, 'Joseph Kwabena Fosu Okyere', 3),
(134, 'Nii Aryee Aryeetey', 3),
(135, 'Shedika Baburononi Hassan', 3),
(136, 'Dominic Aboagye', 3),
(137, 'Edith Yaa Okyerewa Boakye', 3),
(138, 'Emmanuel Annor', 3),
(139, 'Mariam Korankye', 2),
(140, 'Eric Acheampong', 2),
(141, 'Eunice Tachie-Menson', 3),
(142, 'Edward Laryea', 3),
(143, 'Klenam Sedegah', 3),
(144, 'Rahmatu Alhassan Fynn', 3),
(145, 'Betty Blankson', 3),
(146, 'Edna Boa Amponsem', 3),
(147, 'Mahdi Jamaldeen', 3),
(148, 'Perpetual Asante', 1),
(149, 'Laila Duwiejua', 1),
(150, 'David Paapa Asante-Asare', 1),
(151, 'Richmond Agbelengor', 1),
(152, 'Joojo Afun', 1),
(153, 'Acheampong Yaw Amoateng', 1),
(154, 'Twene Osei', 1),
(155, 'Anthony Abeo', 1),
(156, 'Abigail Awuah', 1),
(157, 'Affum Alhassan', 1),
(158, 'Aurelia Ayisi', 1),
(159, 'Danyuo Yiporo', 1),
(160, 'David Hutchful', 1),
(161, 'Elizabeth Johnson', 1),
(162, 'Elsie Aminarh', 1),
(163, 'Emmanuel Kojo Aidoo', 1),
(164, 'Emmanuel Obeng Ntow', 1),
(165, 'Eric Gadzi', 1),
(166, 'Eugene Daniels', 1),
(167, 'Iréné Amessouwoe', 1),
(168, 'Jean Avaala', 1),
(169, 'Joseph Atatsi', 1),
(170, 'Jude Samuel Acquaah', 1),
(171, 'Knowledge Ahadzitse', 3),
(172, 'Kwaku Yamoah', 1),
(173, 'Mariam Korankye', 1),
(174, 'Mensimah Thompson Kwaffo', 1),
(175, 'Millicent Adjei', 1),
(176, 'Tatenda Kavu', 1),
(177, 'William Hoskins', 1),
(178, 'Yaw Mpeani-Brantuo', 1),
(179, 'Yvonne Dewortor', 1);


INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (442, 'Keren Arthur', 3),
    (443, 'Aisha Fremah Yeboah Ansah', 3),
    (444, 'Nana Kwasi Karikari', 1);

INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (944, 'Adwoa Opoku-Agyemang', 1);

INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (945, 'Nicholas Tali', 1);

INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (946, 'Peter Lawerh Kwao', 3);

INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (947, 'Yamoah Frimpong Attafuah', 3);

INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (960, 'Abraham Joojo Afun', 3);

INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (961, 'Prisca Amponsah', 3);






INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (700, 'Amma Gyaama Kuma', 3),
    (180, 'Benjamin Dzivenu Akakpo', 3),
    (181, 'Abdul-Karim Ngoliba', 3),
    (182, 'Abigail Awuah', 3),
    (183, 'Adelle Maame Ama Barko Hasford', 3),
    (184, 'Alfred Berkoh', 3),
    (185, 'Alhassan Hassan', 3),
    (186, 'Annaliese Susan Blessing Korkor Nartey', 3),
    (187, 'Anthony Aninagyei', 3),
    (188, 'Benjamin Dzivenu Akakpo', 3),
    (189, 'Brenda Adjoa Gerbs', 3),
    (190, 'Clifford Yeboah', 3),
    (191, 'Daniel Mawuli Seworye', 3),
    (192, 'Delali Esi Enyonam Segbor', 3),
    (193, 'Derrick Addo-Aikins', 3),
    (194, 'Edna Naa Tetteh', 3),
    (195, 'Enoch Nganigme Aho', 3),
    (196, 'Erica Naa Kai Anang', 3),
    (197, 'Eugene Eluerkeh', 3),
    (198, 'Eyram Tawia', 3),
    (199, 'Felicia Engmann', 3),
    (200, 'Fortune Amenuvor', 3),
    (201, 'Gerhard Nana Addo Opare-Addo', 3),
    (202, 'Hafiz Adjei', 3),
    (203, 'Hassana Mahama', 3),
    (204, 'Henry Owusu', 3),
    (205, 'Isabella Sompa Twum-Antwi', 3),
    (206, 'Jadis Azade Aganda', 3),
    (207, 'James Abugre', 3),
    (208, 'Joe Ghartey', 3),
    (209, 'Joel Osei-Asamoah', 3),
    (210, 'John Terence Manful', 3),
    (211, 'Joseph Mensah Asare', 3),
    (212, 'Kojo Anyinam-Boateng', 3),
    (213, 'Kwadwo Asare Debrah', 3),
    (214, 'Leanne Maame Mozuma Annor-Adjaye', 3),
    (215, 'Maureen Kyere', 3),
    (216, 'Naa Dromo Aryee', 3),
    (217, 'Nana Amma Opoku-Boadu', 3),
    (218, 'Natasha Skult', 3),
    (219, 'Nathalie Blandine N''Guessan', 3),
    (220, 'Nii-Tete Yartey', 3),
    (221, 'Oheneba Dade', 3),
    (222, 'Olaf Hall-Holt', 3),
    (223, 'Philip Asare', 3),
    (224, 'Phoebe Nuoyong Continua', 3),
    (225, 'Pius Gadosey', 3),
    (226, 'Raymond Honu', 3),
    (227, 'Reynolds Okyere Boakye', 3),
    (228, 'Samuel Kwame Osei Blankson', 3),
    (229, 'Samuel Kwasi Asiedu Awuah', 3),
    (230, 'Selasi Kwaku Ocloo', 3),
    (231, 'Siphiwe Abraham', 3),
    (232, 'Stanley Agudu', 3),
    (233, 'Stephen Nii Adu Tagoe', 3),
    (234, 'Suzette Carlotta Zwennes', 3),
    (235, 'Thelma Boakyewaa Asiedu', 3),
    (236, 'Thomas Kojo Yesu Quarshie', 3),
    (237, 'Tiffany Ampene', 3),
    (238, 'Wendy Osei', 3),
    (239, 'William Akuffo', 3),
    (240, 'Yasmin Angaa-Mwini Kamal-Deen Gbontaa', 3),
    (241, 'Jamal-Deen Abdulai', 3),
    (242, 'Facilitator A', 1),
    (243, 'Facilitator B', 1),
    (244, 'Facilitator C', 1),
    (245, 'Facilitator D', 1),
    (246, 'Facilitator E', 1),
    (247, 'Facilitator F', 1),
    (248, 'Facilitator G', 1),
    (249, 'Facilitator H', 1),
    (250, 'Facilitator I', 1),
    (251, 'Facilitator J', 1),
    (252, 'Facilitator K', 1),
    (253, 'Facilitator L', 1);

INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (254, 'Facilitator M', 1),
    (255, 'Facilitator N', 1),
    (256, 'Facilitator O', 1),
    (257, 'Facilitator P', 1),
    (258, 'Facilitator Q', 1),
    (259, 'Facilitator R', 1),
    (260, 'Facilitator S', 1),
    (261, 'Facilitator T', 1);



INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES (262, 'None', 3);

INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (777, 'Mohammed Elmir', 3);

INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (790, 'Victoria Osei-Bonsu', 1);

INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (807, 'Hassana Mahama', 1);

INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (810, 'Joseph Kwabena Fosu  Okyere', 3);

INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (809, 'Noah Adasi', 3);


INSERT INTO Lecturer (LecturerID, LecturerName, FacultyTypeID)
VALUES
    (811, 'Bright Anim Antwi', 3);






CREATE TABLE Duration (
    DurationID INT PRIMARY KEY AUTO_INCREMENT,
    Duration TIME NOT NULL
) ENGINE=InnoDB;

INSERT INTO Duration (Duration) 
VALUES 
('01:00:00'),
('01:30:00'),
('03:00:00'),
('02:00:00'),
('01:45:00'),
('03:15:00');

CREATE TABLE Course (
    CourseID INT PRIMARY KEY AUTO_INCREMENT,
    CourseCode VARCHAR(255) NOT NULL UNIQUE,
    CourseName VARCHAR(255) NOT NULL,
    RequirementType VARCHAR(255) NOT NULL,
    ActiveFlag TINYINT NOT NULL,
    Credits DECIMAL(5,2) NOT NULL
) ENGINE=InnoDB;

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES
(1, 'ENGL112', 'Written and Oral Communication', 'Core', 1, 1.0),
(2, 'ENGL113', 'Text & Meaning', 'Core', 1, 1.0),
(3, 'BUSA161', 'Foundations of Design and Entrepreneurship I', 'Core', 1, 1.0),
(4, 'BUSA162', 'Foundations of Design and Entrepreneurship II', 'Core', 1, 1.0),
(5, 'ECON101', 'Microeconomics', 'Core', 1, 1.0),
(6, 'SOAN121', 'Social Theory', 'Core', 1, 1.0),
(7, 'SOAN111', 'Leadership Seminar 1: What Makes a Good Leader?', 'Core', 1, 0.5),
(8, 'SOAN211', 'Leadership Seminar 2: Rights, Ethics, and Rule of Law', 'Core', 1, 0.5),
(9, 'SOAN311', 'Leadership Seminar 3: The Economic Development of a Good Society', 'Core', 1, 0.5),
(10, 'SOAN411', 'Leadership Seminar 4 for Engineers: Leadership as Service', 'Core', 1, 1.0),
(11, 'POLS231_202', 'Pan-Africanism', 'Elective', 1, 1.0),
(12, 'ENG215', 'African Literature', 'Elective', 1, 1.0),
(13, 'MATH141', 'Calculus 1', 'Core', 1, 1.0),
(14, 'MATH142', 'Calculus 2', 'Core', 1, 1.0),
(15, 'MATH152', 'Statistics for Engineering and Economics', 'Core', 1, 1.0),
(16, 'MATH211', 'Multivariable Calculus and Linear Algebra', 'Core', 1, 1.0),
(17, 'MATH221', 'Statistics with Probability', 'Core', 1, 1.0),
(18, 'CS112', 'Computer Programming for Engineering', 'Core', 1, 1.0),
(19, 'SC112', 'Physics I: Mechanics', 'Core', 1, 1.0),
(20, 'SC113', 'Physics II: Electromagnetism', 'Core', 1, 1.0),
(21, 'SC221', 'Materials Science & Chemistry', 'Core', 1, 1.0),
(22, 'CS222', 'Data Structures and Algorithms', 'Core', 1, 1.0),
(23, 'CS415', 'Software Engineering', 'Core', 1, 1.0),
(24, 'CS432', 'Networks and Distributed Computing', 'Core', 1, 1.0),
(25, 'BUSA304', 'Operations Management', 'Elective', 1, 1.0),
(26, 'BUSA444', 'Supply Chain Management', 'Elective', 1, 1.0),
(27, 'CS223', 'Algorithms', 'Core', 1, 1.0),
(29, 'CS331', 'Computer Architecture', 'Core', 1, 1.0),
(30, 'CS333', 'Operating Systems', 'Core', 1, 1.0),
(31, 'CS341', 'Web Development', 'Elective', 1, 1.0),
(32, 'CS353', 'Introduction to AI Robotics', 'Elective', 1, 1.0),
(33, 'BUSA201', 'Financial Accounting', 'Core', 1, 1.0),
(34, 'BUSA311', 'Managerial Accounting', 'Core', 1, 1.0),
(35, 'BUSA341', 'Marketing', 'Core', 1, 1.0),
(36, 'BUSA204', 'Business Strategy', 'Core', 1, 1.0),
(37, 'EE201', 'Introduction to Electrical Circuits', 'Core', 1, 1.0),
(38, 'EE301', 'Power Systems', 'Core', 1, 1.0),
(39, 'ME101', 'Introduction to Mechanics', 'Core', 1, 1.0),
(40, 'ME201', 'Thermodynamics', 'Core', 1, 1.0),
(42, 'MIS201', 'Enterprise Systems', 'Core', 1, 1.0),
(43, 'BUSA132', 'Organizational Behavior', 'Core', 1, 1.0),
(45, 'BUSA350', 'International Trade & Policy', 'Core', 1, 1.0),
(46, 'BUSA323', 'Corporate Finance', 'Core', 1, 1.0),
(48, 'SC231', 'Introduction to Chemistry', 'Core', 1, 1.0),
(49, 'ENG101', 'English Composition', 'Core', 1, 1.0),
(51, 'EE451', 'Power Engineering', 'Elective', 1, 1.0),
(52, 'CS453', 'Robotics', 'Elective', 1, 1.0),
(53, 'ME431', 'Fluid Mechanics', 'Core', 1, 1.0),
(55, 'CS457', 'Data Mining', 'Elective', 1, 1.0),
(57, 'SOAN233', 'African Music and Dance', 'Elective', 1, 1.0),
(58, 'POLS233', 'African Philosophy', 'Elective', 1, 1.0),
(59, 'ECON102', 'Macroeconomics', 'Core', 1, 1.0),
(60, 'SOAN229', 'Social Research Methods', 'Core', 1, 1.0),
(61, 'MATH144', 'Applied Calculus', 'Core', 1, 1.0),
(62, 'ENGR112', 'Introduction to Engineering', 'Core', 1, 1.0),
(63, 'ENGR311', 'System Dynamics', 'Core', 1, 1.0),
(64, 'ENGR312', 'Control Systems', 'Core', 1, 1.0),
(65, 'ENGR413', 'Project Management', 'Core', 1, 1.0),
(66, 'CS454', 'Artificial Intelligence', 'Elective', 1, 1.0),
(68, 'CS424', 'Advanced Database Systems', 'Elective', 1, 1.0),
(700, 'BUSA455', 'Project Management', 'Elective', 1, 1.0),
(69, 'CS451', 'Computer Graphics', 'Elective', 1, 1.0),
(71, 'ECON321', ' Econometrics I', 'Elective', 1, 1.0),
(72, 'ECON341', 'Operations Research', 'Elective', 1, 1.0),
(74, 'BUSA401_A', 'Entrepreneurship I', 'Capstone', 1, 1.0),
(75, 'BUSA401_B', 'Entrepreneurship II', 'Capstone', 1, 1.0),
(76, 'CS400_A', 'Thesis I', 'Capstone', 1, 1.0),
(77, 'CS400_B', 'Thesis II', 'Capstone', 1, 1.0),
(78, 'BUSA411', 'Applied Senior Project I', 'Core', 1, 1.0),
(79, 'MIS301', 'E-commerce', 'Core', 1, 1.0),
(80, 'MIS302', 'Advanced Database Systems', 'Core', 1, 1.0),
(81, 'MIS303', 'Networks and Distributed Computing', 'Core', 1, 1.0),
(82, 'MIS304', 'Programming II', 'Core', 1, 1.0),
(83, 'BUSA442', 'Strategic Brand Management', 'Elective', 1, 1.0),
(84, 'BUSA462', 'New Product Development', 'Elective', 1, 1.0),
(85, 'ENGR300', 'Third Year Group Project & Seminar', 'Core', 1, 0.5),
(86, 'CE122', 'Applied Programming for Engineers', 'Core', 1, 0.5),
(87, 'ENGR212', 'Instrumentation for Engineering', 'Core', 1, 0.5),
(88, 'CE322', 'Digital Systems Design', 'Core', 1, 1.0),
(89, 'CE451', 'Embedded Systems', 'Core', 1, 1.0),
(90, 'CS313', 'Intermediate Computer Programming', 'Core', 1, 1.0),
(92, 'CS433', 'Operating Systems and Systems Administration', 'Core', 1, 1.0),
(93, 'CS456', 'Algorithm Design & Analysis', 'Core', 1, 1.0),
(94, 'ME311', 'Mechanics of Materials/Structural Engineering', 'Core', 1, 1.0),
(95, 'ME301', 'Mechanical Machine Design', 'Core', 1, 1.0),
(97, 'ME421', 'Thermal Systems and Applications', 'Core', 1, 1.0),
(99, 'EE222', 'Circuits and Electronics', 'Core', 1, 1.0),
(100, 'EE242', 'Introduction to Electrical Machines and Power Electronics', 'Core', 1, 1.0),
(101, 'EE342', 'Advanced Electrical Machines and Power Electronics', 'Core', 1, 1.0),
(102, 'EE453', 'Power Systems Analysis', 'Elective', 1, 1.0),
(104, 'CS412', 'Concepts of Programming Languages', 'Elective', 1, 1.0),
(106, 'CS443', 'Mobile App Development', 'Elective', 1, 1.0),
(108, 'CS455', 'Applied Cryptography and Security', 'Elective', 1, 1.0),
(111, 'ENGR400', 'Senior Project', 'Capstone', 1, 1.0),
(112, 'ENGR401', 'Senior Project and Seminar', 'Capstone', 1, 1.0),
(113, 'ENGR414', 'Environmental Science and Engineering', 'Elective', 1, 1.0),
(114, 'SC141', 'Introduction to Biology', 'Core', 1, 1.0),
(115, 'SC241', 'Biochemistry', 'Core', 1, 1.0),
(116, 'SC341', 'Molecular Biology', 'Core', 1, 1.0),
(118, 'ENGR313', 'Project Management', 'Core', 1, 1.0),
(119, 'EE421', 'Digital and Analog Signal Processing', 'Elective', 1, 1.0),
(120, 'CS451', 'VLSI: Embedded Systems', 'Elective', 1, 1.0),
(121, 'CS311', 'Theory of Computation', 'Core', 1, 1.0),
(122, 'MIS101', 'Introduction to Information Systems', 'Core', 1, 1.0),
(123, 'MIS401', 'Thesis in MIS', 'Capstone', 1, 1.0),
(124, 'MIS402', 'Thesis II in MIS', 'Capstone', 1, 1.0),
(125, 'CS417', 'Computational Theory', 'Core', 1, 1.0),
(126, 'CS425', 'Distributed Systems', 'Elective', 1, 1.0),
(127, 'CS435', 'Cloud Computing', 'Elective', 1, 1.0),
(128, 'CS452', 'Machine Learning', 'Elective', 1, 1.0),
(129, 'CS459', 'Deep Learning', 'Elective', 1, 1.0),
(130, 'CS314', 'Human-Computer Interaction', 'Core', 1, 1.0),
(133, 'SC112', 'Physics 1', 'Core', 1, 1.0),
(134, 'SC113', 'Physics 2', 'Core', 1, 1.0),
(135, 'CS121', 'Introduction to Programming', 'Core', 1, 1.0),
(136, 'CS211', 'Data Analytics', 'Elective', 1, 1.0),
(137, 'CS441', 'Information Security', 'Elective', 1, 1.0),
(138, 'BUSA401_C', 'Leadership for Entrepreneurs', 'Capstone', 1, 1.0),
(139, 'ENG101', 'Introduction to Technical Writing', 'Core', 1, 1.0),
(140, 'CS200', 'Game Design', 'Elective', 1, 1.0),
(141, 'CS401', 'Mobile Computing', 'Elective', 1, 1.0),
(142, 'CS404', 'Big Data Analytics', 'Elective', 1, 1.0),
(143, 'CS440', 'Blockchain Technologies', 'Elective', 1, 1.0),
(144, 'CS442', 'Advanced Networking', 'Elective', 1, 1.0),
(145, 'ENG200', 'Engineering Ethics', 'Core', 1, 1.0),
(146, 'EE311', 'Communication Systems', 'Core', 1, 1.0),
(147, 'BUSA100', 'Business Fundamentals', 'Core', 1, 1.0),
(148, 'BUSA101', 'Introduction to Accounting', 'Core', 1, 1.0),
(149, 'CS456', 'Algorithm Design', 'Core', 1, 1.0),
(151, 'ENGR411', 'Advanced Control Systems', 'Elective', 1, 1.0),
(152, 'ENGR501', 'Microcontroller Programming', 'Elective', 1, 1.0),
(153, 'ENGR502', 'Advanced Robotics', 'Elective', 1, 1.0),
(154, 'CS320', 'Data Visualization', 'Elective', 1, 1.0),
(155, 'CS480', 'Capstone Project', 'Capstone', 1, 1.0),
(156, 'MIS210', 'Business Intelligence', 'Core', 1, 1.0),
(157, 'MIS411', 'Information Systems Auditing', 'Elective', 1, 1.0),
(158, 'EE442', 'Power Electronics', 'Core', 1, 1.0),
(159, 'EE450', 'Electromagnetic Field Theory', 'Core', 1, 1.0),
(160, 'EE499', 'Capstone Project in Electrical Engineering', 'Capstone', 1, 1.0),
(161, 'ME422', 'Heat and Mass Transfer', 'Core', 1, 1.0),
(162, 'ME442', 'Computer Aided Design (CAD) / Manufacturing (CAM)', 'Elective', 1, 1.0),
(163, 'BUSA370', 'Innovation and Design Thinking', 'Elective', 1, 1.0),
(164, 'BUSA460', 'International Business', 'Elective', 1, 1.0),
(165, 'SOAN230', 'Cultural Anthropology', 'Elective', 1, 1.0),
(166, 'POLS340', 'International Relations', 'Elective', 1, 1.0),
(167, 'ENG202', 'Scientific Writing', 'Core', 1, 1.0),
(169, 'CS444', 'Advanced Software Engineering', 'Elective', 1, 1.0),
(170, 'CS482', 'Natural Language Processing', 'Elective', 1, 1.0),
(171, 'CS483', 'Computer Vision', 'Elective', 1, 1.0),
(172, 'ME412', 'Advanced Thermodynamics', 'Elective', 1, 1.0),
(173, 'ME450', 'Sustainable Engineering Design', 'Elective', 1, 1.0),
(174, 'BUSA500', 'Global Business Strategy', 'Elective', 1, 1.0),
(175, 'BUSA505', 'Leadership and Ethics', 'Core', 1, 1.0),
(176, 'EE480', 'Advanced Signal Processing', 'Elective', 1, 1.0),
(177, 'SC345', 'Quantum Physics', 'Elective', 1, 1.0),
(178, 'SC350', 'Advanced Material Science', 'Elective', 1, 1.0),
(179, 'BUSA480', 'Entrepreneurial Finance', 'Elective', 1, 1.0),
(180, 'BUSA490', 'Digital Marketing', 'Elective', 1, 1.0),
(181, 'CS474', 'Cybersecurity Management', 'Elective', 1, 1.0),
(182, 'CS470', 'Quantum Computing', 'Elective', 1, 1.0),
(183, 'EE460', 'Smart Grid Technologies', 'Elective', 1, 1.0),
(184, 'EE461', 'Internet of Things (IoT)', 'Elective', 1, 1.0),
(185, 'MIS300', 'Systems Design and Analysis', 'Core', 1, 1.0),
(186, 'MIS401', 'Capstone Project in MIS', 'Capstone', 1, 1.0),
(187, 'MIS402', 'Advanced Business Analytics', 'Elective', 1, 1.0),
(188, 'BUSA410', 'Global Operations Management', 'Elective', 1, 1.0),
(189, 'CS411', 'Advanced Programming Paradigms', 'Elective', 1, 1.0),
(190, 'CS416', 'Machine Learning Operations (MLOps)', 'Elective', 1, 1.0),
(191, 'CS450', 'Big Data Frameworks', 'Elective', 1, 1.0),
(192, 'CS460', 'Blockchain and Cryptocurrency', 'Elective', 1, 1.0),
(193, 'CS465', 'Parallel and Distributed Computing', 'Elective', 1, 1.0),
(194, 'SC400', 'Capstone Project in Sciences', 'Capstone', 1, 1.0),
(195, 'ENGR410', 'Robotics Control Systems', 'Elective', 1, 1.0),
(196, 'ENGR420', 'Autonomous Vehicles', 'Elective', 1, 1.0),
(197, 'EE490', 'Renewable Energy Systems', 'Elective', 1, 1.0),
(198, 'EE495', 'Wireless Communication Systems', 'Elective', 1, 1.0),
(199, 'SC450', 'Advanced Biophysics', 'Elective', 1, 1.0),
(200, 'SC460', 'Nanotechnology', 'Elective', 1, 1.0),
(201, 'MATH212', 'Linear Algebra', 'Core', 1, 1.0),
(202, 'BUSA001', 'Entrepreneurship Universe', 'Core', 1, 1.0),
(203, 'BUSA132', 'Organizational Behaviour', 'Core', 1, 1.0),
(204, 'BUSA210', 'Financial Accounting', 'Core', 1, 1.0),
(205, 'BUSA220', 'Introduction to Finance', 'Core', 1, 1.0),
(206, 'BUSA224', 'Finance for Non-Finance', 'Core', 1, 1.0),
(207, 'BUSA321', 'Investments', 'Core', 1, 1.0),
(208, 'BUSA491', 'Thesis 1', 'Core', 1, 1.0),
(209, 'BUSA402', 'Business Law', 'Core', 1, 1.0),
(210, 'BUSA405', 'Competitive Strategy', 'Core', 1, 1.0),
(211, 'BUSA423', 'International Finance', 'Core', 1, 1.0),
(212, 'BUSA430', 'Human Resource Management', 'Core', 1, 1.0),
(213, 'BUSA431', 'Real Estate Development', 'Elective', 1, 1.0),
(214, 'BUSA442', 'Strategic Brand Management', 'Elective', 1, 1.0),
(215, 'BUSA451', 'Development Economics', 'Elective', 1, 1.0),
(216, 'ECON452', 'Econometrics', 'Elective', 1, 1.0),
(217, 'ECON455', 'Managerial Economics', 'Elective', 1, 1.0),
(218, 'ENGR413', 'Project Management & Professional Practice', 'Elective', 1, 1.0),
(219, 'BUSA425', 'Venture Capital Investment', 'Elective', 1, 1.0),
(220, 'BUSA432', 'Organization Development', 'Elective', 1, 1.0),
(221, 'BUSA441', 'Service Marketing', 'Elective', 1, 1.0),
(222, 'BUSA471', 'Social Enterprise', 'Elective', 1, 1.0),
(223, 'BUS458', 'Data Analytics for Business', 'Elective', 1, 1.0),
(224, 'CS213', 'Object-Oriented Programming', 'Core', 1, 1.0),
(225, 'CS221', 'Discrete Structures and Theory', 'Core', 1, 1.0),
(226, 'CS361', 'Introduction to Modelling and Simulation', 'Elective', 1, 0.5),
(227, 'CS442', 'E-Commerce', 'Elective', 1, 1.0),
(228, 'CS461', 'Data Science', 'Elective', 1, 1.0),
(229, 'IS333', 'IT Infrastructure and Systems Administration', 'Elective', 1, 1.0),
(230, 'IS451', 'Information and Systems Security', 'Elective', 1, 1.0),
(231, 'CS111', 'Introduction to Computing and Information Systems', 'Core', 1, 1.0),
(232, 'CS212', 'Computer Programming for Computer Science', 'Core', 1, 1.0),
(233, 'CS323', 'Database Systems', 'Core', 1, 1.0),
(234, 'CS402', 'CSIS Research Seminar', 'Core', 1, 0.0),
(235, 'CS434', 'Parallel & Distributed Computing', 'Elective', 1, 1.0),
(236, 'CS462', 'Cloud Computing', 'Elective', 1, 1.0),
(237, 'IS371', 'Technology & Ethics', 'Elective', 1, 1.0),
(238, 'IS361', 'IS Project Management', 'Elective', 1, 1.0),
(239, 'CS354', 'Computer Game Development', 'Elective', 1, 1.0),
(240, 'AS111', 'Ashesi Success', 'Core', 1, 0.0),
(241, 'BUSA492', 'Thesis 2', 'Core', 1, 1.0),
(878, 'BUSA412', 'Applied Senior Project II', 'Core', 1, 1.0),
(242, 'MATH121', 'Pre-calculus 1', 'Core', 1, 1.0),
(243, 'MATH122', 'Pre-calculus 2', 'Core', 1, 1.0),
(244, 'MATH223', 'Quantitative Methods', 'Core', 1, 1.0),
(245, 'BUSA220', 'Introduction to Finance', 'Core', 1, 1.0),
(246, 'SOAN325', 'Research Methods', 'Core', 1, 1.0),
(247, 'ECON100', 'Principles of Economics', 'Core', 1, 1.0),
(248, 'CS254', 'Introduction to Artificial Intelligence', 'Core', 1, 1.0),
(249, 'CS330', 'Hardware and Systems Fundamentals', 'Core', 1, 1.0),
(250, 'CS432', 'Computer Networks and Data Communications', 'Core', 1, 1.0),
(251, 'CS410', 'Applied Project', 'Core', 1, 1.0),
(252, 'MATH161', 'Engineering Calculus', 'Core', 1, 1.0),
(253, 'MATH251', 'Differential Equations & Numerical Methods', 'Core', 1, 1.0),
(254, 'EE341', 'AC Electrical Machines', 'Core', 1, 1.0),
(255, 'EE320', 'Signals & Systems', 'Core', 1, 1.0),
(256, 'EE321', 'Communication Systems', 'Core', 1, 1.0),
(257, 'ME441', 'Manufacturing Processes', 'Core', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES
(500, 'AV100', 'Ashesi Voices', 'Elective', 1, 1.0),
(501, 'EE422', 'Advanced Communication Systems', 'Elective', 1, 1.0),
(502, 'ENGR444', 'Automation and Production Systems', 'Elective', 1, 1.0),
(503, 'FRENC111', 'Introductory French I', 'Elective', 1, 1.0),
(504, 'FRENC122', 'Professional French I', 'Elective', 1, 1.0),
(505, 'POLS322', 'China-Africa Relations', 'Elective', 1, 1.0),
(506, 'POLS334', 'Introduction to Public Policy', 'Elective', 1, 1.0),
(507, 'SOAN322', 'African Cultural Institutions', 'Elective', 1, 1.0),
(508, 'SOAN320', 'World Hunger, Population and Food Supplies', 'Elective', 1, 1.0),
(509, 'SOAN331', 'Climate Change and Global Innovation', 'Elective', 1, 1.0),
(510, 'SOAN328', 'Creative and Research Internship', 'Elective', 1, 1.0),
(511, 'IS362', 'IS Project Management', 'Elective', 1, 1.0),
(512, 'ME401', 'Mechanics of Machines & Engineering Vibration', 'Elective', 1, 1.0),
(513, 'ME445', 'Machine Shop and Factory Design', 'Elective', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES
(258, 'BUSA231', 'Business Communication and Negotiations', 'Core', 1, 1.0);

INSERT INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES ('ELECTIVE1', 'Major Elective', 'Elective', 1, 1.0);

INSERT INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES ('ELECTIVE2', 'Non-Major Elective', 'Elective', 1, 1.0);

-- Insert the new "Elective" course
INSERT INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES (
    'ELECTIVE', 
    'Major or Non-Major Elective', 
    'Elective', 
    1, 
    1.0
);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES
(290, 'SOAN301', 'Introduction to Africana Studies: The Global Black Experience', 'Elective', 1, 1.0);

INSERT INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES
    (900, 'BUSA446', 'Integrated Marketing Communications', 'Elective', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES (300, 'MATH101', 'College Algebra', 'Core', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES (321, 'EE454', 'Renewable Energy and Smart Grid', 'Elective', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES (352, 'ME444', 'Advanced Mechanical Machine Design', 'Elective', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES (343, 'SOAN251', 'Africa in the International Setting', 'Elective', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES (304, 'ECON231', 'Mathematics for Economists', 'Core', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES (376, 'ME434', 'Hydraulic & Fluid Machinery', 'Elective', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES (430, 'ENGR412', 'Synthetic Biological Engineering', 'Elective', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES (470, 'ENGR461', 'Financial Engineering', 'Elective', 1, 1.0);

INSERT IGNORE INTO Course (CourseID, CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES
    (261, 'IS351', 'Systems Analysis and Design', 'Core', 1, 1.0);

INSERT IGNORE INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES
    ('ECON302', 'Intermediate Microeconomic Theory II', 'Elective', 1, 1.0),
    ('ECON304', 'Intermediate Macroeconomic Theory II', 'Elective', 1, 1.0),
    ('ECON202', 'Principles of Macroeconomics', 'Elective', 1, 1.0),
    ('ECON211', 'The Economy of Ghana', 'Elective', 1, 1.0),
    ('ECON241', 'Introduction to Environmental Economics', 'Elective', 1, 1.0);


INSERT IGNORE INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES
    ('LLB111', 'Language for Law', 'Core', 1, 1.0),
    ('LLB112', 'Ghana Legal System & Methods', 'Core', 1, 1.0),
    ('LLB114', 'Legal Writing', 'Core', 1, 1.0),
    ('LLB150', 'Introduction to Public Policy', 'Core', 1, 1.0),
    ('LLB213', 'Constitutional Law I', 'Core', 1, 1.0),
    ('LLB215', 'Contract Law I', 'Core', 1, 1.0);

-- Insert POLS221 - African Philosophical Thought
INSERT INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES ('POLS221', 'African Philosophical Thought', 'Elective', 1, 1.0);

-- Insert POLS222 - Political Economy of Healthcare in Ghana
INSERT INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES ('POLS222', 'Political Economy of Healthcare in Ghana', 'Elective', 1, 1.0);

INSERT INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES ('ME432', 'Computational Fluid Dynamics', 'Elective', 1, 1.0);

-- Insert the new elective course
INSERT INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES ('SOAN332', 'Sustainability and Systems Thinking', 'Elective', 1, 1.0);

-- Insert all four elective courses at once
INSERT INTO Course (CourseCode, CourseName, RequirementType, ActiveFlag, Credits)
VALUES 
    ('SOAN225', 'Ghanaian Popular Culture', 'Elective', 1, 1.0),
    ('SOAN236', 'ESG: Corporate Ethics in Africa', 'Elective', 1, 1.0),
    ('SOAN239', 'African & Diasporan Choir', 'Elective', 1, 1.0),
    ('SOAN242', 'Modern Dance Traditions of Ghana', 'Elective', 1, 1.0);


CREATE TABLE Cohort (
    CohortID INT PRIMARY KEY AUTO_INCREMENT,
    CohortName VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

-- Populate Cohort table with Cohorts A to Z
INSERT INTO Cohort (CohortID, CohortName)
VALUES
(1, 'Section A'),
(2, 'Section B'),
(3, 'Section C'),
(4, 'Section D'),
(5, 'Section E'),
(6, 'Section F'),
(7, 'Section G'),
(8, 'Section H'),
(9, 'Section I'),
(10, 'Section J'),
(11, 'Section K'),
(12, 'Section L'),
(13, 'Section M'),
(14, 'Section N'),
(15, 'Section O'),
(16, 'Section P'),
(17, 'Section Q'),
(18, 'Section R'),
(19, 'Section S'),
(20, 'Section T'),
(21, 'Section U'),
(22, 'Section V'),
(23, 'Section W'),
(24, 'Section X'),
(25, 'Section Y'),
(26, 'Section Z');


CREATE TABLE SessionAssignments (
    SessionID INT PRIMARY KEY AUTO_INCREMENT,
    CourseCode VARCHAR(20) NOT NULL,
    LecturerName VARCHAR(100) NOT NULL,
    CohortName VARCHAR(50) NOT NULL,
    SessionType VARCHAR(50) NOT NULL,
    Duration TIME NOT NULL,
    NumberOfEnrollments INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;




CREATE TABLE SessionSchedule (
    ScheduleID INT PRIMARY KEY AUTO_INCREMENT,
    SessionID INT NOT NULL,
    DayOfWeek ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday') NOT NULL,
    StartTime TIME NOT NULL,
    EndTime TIME NOT NULL,
    RoomName VARCHAR(255) NOT NULL,
    FOREIGN KEY (SessionID) REFERENCES SessionAssignments(SessionID)
) ENGINE=InnoDB;

CREATE TABLE Major (
    MajorID INT PRIMARY KEY AUTO_INCREMENT,
    MajorName VARCHAR(255) NOT NULL UNIQUE
) ENGINE=InnoDB;

INSERT INTO Major (MajorID, MajorName)
VALUES
(1, 'Business Administration'),
(2, 'Computer Science'),
(3, 'Management Information Systems (MIS)'),
(4, 'Computer Engineering'),
(5, 'Mechatronics Engineering'),
(6, 'Mechanical Engineering'),
(7, 'Electrical and Electronic Engineering'),
(8, 'Law with Public Policy');

ALTER TABLE Lecturer ADD COLUMN ActiveFlag INTEGER NOT NULL DEFAULT 1 CHECK (ActiveFlag IN (0, 1));
ALTER TABLE Room ADD COLUMN ActiveFlag INTEGER NOT NULL DEFAULT 1 CHECK (ActiveFlag IN (0, 1));

ALTER TABLE SessionAssignments
ADD COLUMN NumberOfEnrollments INT NOT NULL DEFAULT 0;




UPDATE Room
SET ActiveFlag = 1;

-- -----------------------------------------
-- 1. Create the Student table
-- -----------------------------------------
CREATE TABLE Student (
    StudentID INT PRIMARY KEY AUTO_INCREMENT,
    MajorID INT NOT NULL,
    YearNumber INT NOT NULL,
    FOREIGN KEY (MajorID) REFERENCES Major(MajorID)
) ENGINE=InnoDB;

-- -----------------------------------------
-- 2. Populate Student table with all
--    possible Major + Year combos
--    (8 majors x 4 years = 32 rows)
-- -----------------------------------------
INSERT INTO Student (MajorID, YearNumber)
VALUES
    -- Business Administration (MajorID=1), Years 1-4
    (1, 1), (1, 2), (1, 3), (1, 4),
    -- Computer Science (MajorID=2), Years 1-4
    (2, 1), (2, 2), (2, 3), (2, 4),
    -- Management Information Systems (MIS) (MajorID=3), Years 1-4
    (3, 1), (3, 2), (3, 3), (3, 4),
    -- Computer Engineering (MajorID=4), Years 1-4
    (4, 1), (4, 2), (4, 3), (4, 4),
    -- Mechatronics Engineering (MajorID=5), Years 1-4
    (5, 1), (5, 2), (5, 3), (5, 4),
    -- Mechanical Engineering (MajorID=6), Years 1-4
    (6, 1), (6, 2), (6, 3), (6, 4),
    -- Electrical and Electronic Engineering (MajorID=7), Years 1-4
    (7, 1), (7, 2), (7, 3), (7, 4),
    -- Law with Public Policy (MajorID=8), Years 1-4
    (8, 1), (8, 2), (8, 3), (8, 4);

CREATE TABLE StudentCourseSelection (
    SelectionID INT PRIMARY KEY AUTO_INCREMENT,
    StudentID INT NOT NULL,
    CourseCode VARCHAR(255) NOT NULL,
    FOREIGN KEY (StudentID) REFERENCES Student(StudentID),
    FOREIGN KEY (CourseCode) REFERENCES Course(CourseCode)
) ENGINE=InnoDB;

ALTER TABLE StudentCourseSelection
ADD COLUMN Type ENUM(
    'No Subtype', 
    'Type I', 'Type II', 'Type III', 'Type IV', 'Type V', 
    'Type VI', 'Type VII', 'Type VIII', 'Type IX', 'Type X'
) NOT NULL DEFAULT 'No Subtype';

CREATE TABLE UnassignedSessions (
    SessionID INT PRIMARY KEY AUTO_INCREMENT,
    CourseCode VARCHAR(20) NOT NULL,
    LecturerName VARCHAR(100) NOT NULL,
    CohortName VARCHAR(50) NOT NULL,
    SessionType VARCHAR(50) NOT NULL,
    Duration TIME NOT NULL,
    NumberOfEnrollments INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

--
-- 1) Create the ProgramPlan table
--
CREATE TABLE ProgramPlan (
    ProgramPlanID INT PRIMARY KEY AUTO_INCREMENT,
    MajorID INT NOT NULL,
    YearNumber INT NOT NULL,
    SemesterNumber INT NOT NULL,
    SubType VARCHAR(50) NULL,  -- "I", "II", "III", or NULL
    CourseCode VARCHAR(255) NOT NULL,

    FOREIGN KEY (MajorID) REFERENCES Major(MajorID),
    FOREIGN KEY (CourseCode) REFERENCES Course(CourseCode)
) ENGINE=InnoDB;


-- Add Program Plans for Electrical and Electronic Engineering (MajorID=7)

-- Year 1, Semester 1
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 1, 1, '', 'AS111'),
    (7, 1, 1, '', 'ENGL112'),
    (7, 1, 1, '', 'BUSA161'),
    (7, 1, 1, '', 'ENGR112'),
    (7, 1, 1, '', 'MATH161');

-- Year 1, Semester 2
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 1, 2, '', 'CS112'),
    (7, 1, 2, '', 'MATH211'),
    (7, 1, 2, '', 'BUSA162'),
    (7, 1, 2, '', 'ME101'),
    (7, 1, 2, '', 'SOAN111');

-- Year 2, Semester 3
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 2, 3, '', 'SC113'),
    (7, 2, 3, '', 'ME201'),
    (7, 2, 3, '', 'MATH152'),
    (7, 2, 3, '', 'SOAN211'),
    (7, 2, 3, '', 'ME442');

-- Year 2, Semester 4
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 2, 4, '', 'MATH251'),
    (7, 2, 4, '', 'SOAN311'),
    (7, 2, 4, '', 'EE222'),
    (7, 2, 4, '', 'SC221'),
    (7, 2, 4, '', 'ENGL113'),
    (7, 2, 4, '', 'CE122');

-- Year 3, Semester 5
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 3, 5, '', 'EE341'),
    (7, 3, 5, '', 'ENGR311'),
    (7, 3, 5, '', 'SOAN411'),
    (7, 3, 5, '', 'ENGR212'),
    (7, 3, 5, '', 'ENGR300'),
    (7, 3, 5, '', 'EE320');

-- Year 3, Semester 6
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 3, 6, '', 'ENGR312'),
    (7, 3, 6, '', 'EE342'),
    (7, 3, 6, '', 'CE322'),
    (7, 3, 6, '', 'EE321'),
    (7, 3, 6, '', 'ELECTIVE1');

-- Year 4, Semester 7
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 4, 7, '', 'EE451'),
    (7, 4, 7, '', 'ELECTIVE1'),
    (7, 4, 7, '', 'ECON100'),
    (7, 4, 7, '', 'CE451'),
    (7, 4, 7, '', 'ELECTIVE');

-- Year 4, Semester 8
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (7, 4, 8, '', 'ENGR413'),
    (7, 4, 8, '', 'ELECTIVE1'),
    (7, 4, 8, '', 'ELECTIVE2'),
    (7, 4, 8, '', 'ENGR401');


--- BUSINESS ADMINISTRATION

-- Year 1, Semester 1 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 1, 1, 'I', 'AS111'),    -- Ashesi Success
(1, 1, 1, 'I', 'MATH121'),  -- Pre-calculus 1
(1, 1, 1, 'I', 'ENGL112'),  -- Written and Oral Communication
(1, 1, 1, 'I', 'BUSA161'),  -- Foundations of Design and Entrepreneurship I
(1, 1, 1, 'I', 'CS111');    -- Introduction to Computing and Information Systems

-- Year 1, Semester 1 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 1, 1, 'II', 'AS111'),
(1, 1, 1, 'II', 'MATH141'),
(1, 1, 1, 'II', 'ENGL112'),
(1, 1, 1, 'II', 'BUSA161'),
(1, 1, 1, 'II', 'CS111');

-- Type III (Introducing MATH101 as an alternative to MATH121)
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (1, 1, 1, 'III', 'AS111'),       -- Ashesi Success
    (1, 1, 1, 'III', 'MATH101'),      -- College Algebra (replaces MATH121)
    (1, 1, 1, 'III', 'ENGL112'),      -- Written and Oral Communication
    (1, 1, 1, 'III', 'BUSA161'),      -- Foundations of Design and Entrepreneurship I
    (1, 1, 1, 'III', 'CS111');        -- Introduction to Computing and Information Systems

-- Year 1, Semester 2 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 1, 2, 'I', 'SOAN111'),
(1, 1, 2, 'I', 'MATH122'),
(1, 1, 2, 'I', 'ENGL113'),
(1, 1, 2, 'I', 'BUSA162');

-- Year 1, Semester 2 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 1, 2, 'II', 'SOAN111'),
(1, 1, 2, 'II', 'MATH142'),
(1, 1, 2, 'II', 'ENGL113'),
(1, 1, 2, 'II', 'BUSA162');

-- Year 2, Semester 3
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 2, 3, '', 'SOAN211'),
(1, 2, 3, '', 'MATH221'),
(1, 2, 3, '', 'ECON101'),
(1, 2, 3, '', 'BUSA210'),
(1, 2, 3, '', 'ELECTIVE2');

-- Year 2, Semester 4
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 2, 4, '', 'SOAN311'),
(1, 2, 4, '', 'MATH223'),
(1, 2, 4, '', 'ECON102'),
(1, 2, 4, '', 'BUSA220'),
(1, 2, 4, '', 'BUSA132');

-- Year 3, Semester 5
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 3, 5, '', 'BUSA304'),
(1, 3, 5, '', 'BUSA350'),
(1, 3, 5, '', 'SOAN411'),
(1, 3, 5, '', 'BUSA341'),
(1, 3, 5, '', 'BUSA422');

-- Year 3, Semester 6
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 3, 6, 'I', 'SOAN325'),
(1, 3, 6, 'I', 'BUSA311'),
(1, 3, 6, 'I', 'SOAN411'),
(1, 3, 6, 'I', 'BUSA323'),
(1, 3, 6, 'I', 'ELECTIVE1');

INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 3, 6, 'II', 'SOAN325'),
(1, 3, 6, 'II', 'BUSA311'),
(1, 3, 6, 'II', 'ELECTIVE'),
(1, 3, 6, 'II', 'BUSA323'),
(1, 3, 6, 'II', 'ELECTIVE1');

-- Year 4, Semester 7 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 4, 7, 'I', 'BUSA405'),
(1, 4, 7, 'I', 'ELECTIVE'),
(1, 4, 7, 'I', 'BUSA321'),
(1, 4, 7, 'I', 'BUSA491');

-- Year 4, Semester 7 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 4, 7, 'II', 'BUSA405'),
(1, 4, 7, 'II', 'ELECTIVE'),
(1, 4, 7, 'II', 'BUSA321'),
(1, 4, 7, 'II', 'BUSA411');

-- Year 4, Semester 7 - Type III
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 4, 7, 'III', 'BUSA405'),
(1, 4, 7, 'III', 'ELECTIVE'),
(1, 4, 7, 'III', 'BUSA321'),
(1, 4, 7, 'III', 'BUSA401_A');
-- Year 4, Semester 8 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 4, 8, 'I', 'BUSA231'),
(1, 4, 8, 'I', 'ELECTIVE'),
(1, 4, 8, 'I', 'ELECTIVE'),
(1, 4, 8, 'I', 'BUSA492');

-- Year 4, Semester 8 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 4, 8, 'II', 'BUSA231'),
(1, 4, 8, 'II', 'ELECTIVE'),
(1, 4, 8, 'II', 'ELECTIVE'),
(1, 4, 8, 'II', 'BUSA412');

-- Year 4, Semester 8 - Type III
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
(1, 4, 8, 'III', 'BUSA231'),
(1, 4, 8, 'III', 'ELECTIVE'),
(1, 4, 8, 'III', 'ELECTIVE'),
(1, 4, 8, 'III', 'BUSA401_B');


-- ----------------------------------------------------
-- Insert Correct ProgramPlan Entries for Computer Science (MajorID = 2)
-- ----------------------------------------------------

-- Year 1
-- Semester 1
-- Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 1, 1, 'I', 'AS111'),       -- Ashesi Success
    (2, 1, 1, 'I', 'MATH121'),     -- Pre-calculus 1
    (2, 1, 1, 'I', 'ENGL112'),     -- Written and Oral Communication
    (2, 1, 1, 'I', 'BUSA161'),     -- Foundations of Design and Entrepreneurship I
    (2, 1, 1, 'I', 'CS111');       -- Introduction to Computing and Information Systems

-- Semester 1
-- Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 1, 1, 'II', 'AS111'),      -- Ashesi Success
    (2, 1, 1, 'II', 'MATH141'),    -- Calculus 1
    (2, 1, 1, 'II', 'ENGL112'),    -- Written and Oral Communication
    (2, 1, 1, 'II', 'BUSA161'),    -- Foundations of Design and Entrepreneurship I
    (2, 1, 1, 'II', 'CS111');      -- Introduction to Computing and Information Systems

-- Type III (Introducing MATH101 as an alternative to MATH121)
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 1, 1, 'III', 'AS111'),       -- Ashesi Success
    (2, 1, 1, 'III', 'MATH101'),      -- College Algebra (replaces MATH121)
    (2, 1, 1, 'III', 'ENGL112'),      -- Written and Oral Communication
    (2, 1, 1, 'III', 'BUSA161'),      -- Foundations of Design and Entrepreneurship I
    (2, 1, 1, 'III', 'CS111');        -- Introduction to Computing and Information Systems

-- Semester 2
-- Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 1, 2, 'I', 'SOAN111'),      -- Leadership Seminar 1: What Makes a Good Leader?
    (2, 1, 2, 'I', 'MATH122'),      -- Pre-calculus 2
    (2, 1, 2, 'I', 'ENGL113'),      -- Text & Meaning
    (2, 1, 2, 'I', 'BUSA162'),      -- Foundations of Design and Entrepreneurship II
    (2, 1, 2, 'I', 'CS212');        -- Computer Programming for Computer Science

-- Semester 2
-- Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 1, 2, 'II', 'SOAN111'),     -- Leadership Seminar 1: What Makes a Good Leader?
    (2, 1, 2, 'II', 'MATH142'),     -- Calculus 2
    (2, 1, 2, 'II', 'ENGL113'),     -- Text & Meaning
    (2, 1, 2, 'II', 'BUSA162'),     -- Foundations of Design and Entrepreneurship II
    (2, 1, 2, 'II', 'CS212');       -- Computer Programming for Computer Science

-- Year 2
-- Semester 3
-- No Type
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 2, 3, '', 'SOAN211'),       -- Leadership Seminar 2: Rights, Ethics, and Rule of Law
    (2, 2, 3, '', 'MATH221'),       -- Statistics with Probability
    (2, 2, 3, '', 'ECON100'),       -- Principles of Economics
    (2, 2, 3, '', 'CS213'),         -- Object-Oriented Programming
    (2, 2, 3, '', 'CS221');         -- Discrete Structures and Theory

-- Semester 4
-- No Type
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 2, 4, '', 'MATH212'),       -- Linear Algebra
    (2, 2, 4, '', 'SOAN311'),       -- Leadership Seminar 3: The Economic Development of a Good Society
    (2, 2, 4, '', 'CS222'),         -- Data Structures and Algorithms
    (2, 2, 4, '', 'CS323'),         -- Database Systems
    (2, 2, 4, '', 'CS254');         -- Introduction to Artificial Intelligence

-- Year 3
-- Semester 5
-- Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 3, 5, 'I', 'SOAN411'),      -- Leadership Seminar 4 for Engineers: Leadership as Service
    (2, 3, 5, 'I', 'CS341'),        -- Web Development
    (2, 3, 5, 'I', 'CS456'),        -- Algorithm Design & Analysis
    (2, 3, 5, 'I', 'CS313'),        -- Intermediate Computer Programming
    (2, 3, 5, 'I', 'CS330');        -- Hardware and Systems Fundamentals

-- Semester 5
-- Type II (Major Elective)
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 3, 5, 'II', 'CS341'),       -- Web Development
    (2, 3, 5, 'II', 'CS456'),       -- Algorithm Design & Analysis
    (2, 3, 5, 'II', 'CS313'),       -- Intermediate Computer Programming
    (2, 3, 5, 'II', 'CS330');       -- Hardware and Systems Fundamentals
    (2, 3, 5, 'II', 'ELECTIVE1'); 

-- Semester 6
-- Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 3, 6, 'I', 'SOAN411'),      -- Leadership Seminar 4 for Engineers: Leadership as Service
    (2, 3, 6, 'I', 'CS415'),        -- Software Engineering
    (2, 3, 6, 'I', 'CS331'),        -- Computer Architecture
    (2, 3, 6, 'I', 'SOAN325'),      -- Research Methods
    (2, 3, 6, 'I', 'CS361');        -- Introduction to Modelling and Simulation

-- Semester 6
-- Type II (Major Elective)
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 3, 6, 'II', 'CS415'),       -- Software Engineering
    (2, 3, 6, 'II', 'CS331'),       -- Computer Architecture
    (2, 3, 6, 'II', 'SOAN325'),     -- Research Methods
    (2, 3, 6, 'II', 'CS361');       -- Introduction to Modelling and Simulation

-- Year 4
-- Semester 7
-- Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 7, 'I', 'CS433'),        -- Operating Systems and Systems Administration
    (2, 4, 7, 'I', 'BUSA224'),      -- Finance for Non-Finance
    (2, 4, 7, 'I', 'CS402'),        -- CSIS Research Seminar
    (2, 4, 7, 'I', 'CS400_A'),      -- Thesis I
    (2, 4, 7, 'I', 'ELECTIVE');      

-- Semester 7
-- Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 7, 'II', 'CS433'),       -- Operating Systems and Systems Administration
    (2, 4, 7, 'II', 'BUSA224'),     -- Finance for Non-Finance
    (2, 4, 7, 'II', 'CS402'),       -- CSIS Research Seminar
    (2, 4, 7, 'II', 'ELECTIVE1'),   -- Extra Major Elective
    (2, 4, 7, 'II', 'ELECTIVE');      

-- Semester 7
-- Type IV
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 7, 'III', 'CS433'),       -- Operating Systems and Systems Administration
    (2, 4, 7, 'III', 'BUSA224'),     -- Finance for Non-Finance
    (2, 4, 7, 'III', 'CS402'),       -- CSIS Research Seminar
    (2, 4, 7, 'III', 'BUSA401_A'),   -- Entrepreneurship I (Capstone)
    (2, 4, 7, 'III', 'ELECTIVE');  

-- Semester 8
-- Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 8, 'I', 'CS432'),        -- Computer Networks and Data Communications
    (2, 4, 8, 'I', 'ELECTIVE'),    -- Elective (4 credits)
    (2, 4, 8, 'I', 'ELECTIVE'),    -- Elective (4 credits)
    (2, 4, 8, 'I', 'CS400_B');      -- Thesis II

-- Semester 8
-- Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 8, 'II', 'CS432'),       -- Computer Networks and Data Communications
    (2, 4, 8, 'II', 'ELECTIVE'),   -- Elective (4 credits)
    (2, 4, 8, 'II', 'ELECTIVE');   -- Elective (4 credits)
  

-- Semester 8
-- Type III
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (2, 4, 8, 'III', 'CS432'),      -- Computer Networks and Data Communications
    (2, 4, 8, 'III', 'ELECTIVE'),  -- Elective (4 credits)
    (2, 4, 8, 'III', 'ELECTIVE'),  -- Elective (4 credits)
    (2, 4, 8, 'III', 'BUSA401_B');  -- Entrepreneurship I (Capstone)

-- MIS

-- Year 1 Semester 1 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 1, 1, 'I', 'AS111'),    -- Ashesi Success
    (3, 1, 1, 'I', 'MATH121'),  -- Pre-calculus 1
    (3, 1, 1, 'I', 'ENGL112'),  -- Written and Oral Communication
    (3, 1, 1, 'I', 'BUSA161'),  -- Foundations of Design and Entrepreneurship I
    (3, 1, 1, 'I', 'CS111');    -- Introduction to Computing and Information Systems

-- Year 1 Semester 1 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 1, 1, 'II', 'AS111'),    -- Ashesi Success
    (3, 1, 1, 'II', 'MATH141'),  -- Calculus 1
    (3, 1, 1, 'II', 'ENGL112'),  -- Written and Oral Communication
    (3, 1, 1, 'II', 'BUSA161'),  -- Foundations of Design and Entrepreneurship I
    (3, 1, 1, 'II', 'CS111');    -- Introduction to Computing and Information Systems

-- Type III (Introducing MATH101 as an alternative to MATH121)
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 1, 1, 'III', 'AS111'),       -- Ashesi Success
    (3, 1, 1, 'III', 'MATH101'),      -- College Algebra (replaces MATH121)
    (3, 1, 1, 'III', 'ENGL112'),      -- Written and Oral Communication
    (3, 1, 1, 'III', 'BUSA161'),      -- Foundations of Design and Entrepreneurship I
    (3, 1, 1, 'III', 'CS111');        -- Introduction to Computing and Information Systems

-- Year 1 Semester 2 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 1, 2, 'I', 'SOAN111'),  -- Leadership Seminar 1: What Makes a Good Leader?
    (3, 1, 2, 'I', 'MATH122'),  -- Pre-calculus 2
    (3, 1, 2, 'I', 'ENGL113'),  -- Text & Meaning
    (3, 1, 2, 'I', 'BUSA162'),  -- Foundations of Design and Entrepreneurship II
    (3, 1, 2, 'I', 'CS212');    -- Computer Programming for Computer Science

-- Year 1 Semester 2 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 1, 2, 'II', 'SOAN111'),  -- Leadership Seminar 1: What Makes a Good Leader?
    (3, 1, 2, 'II', 'MATH142'),  -- Calculus 2
    (3, 1, 2, 'II', 'ENGL113'),  -- Text & Meaning
    (3, 1, 2, 'II', 'BUSA162'),  -- Foundations of Design and Entrepreneurship II
    (3, 1, 2, 'II', 'CS212');    -- Computer Programming for Computer Science

-- Year 2 Semester 3
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 2, 3, '', 'SOAN211'),   -- Leadership Seminar 2: Rights, Ethics, and Rule of Law
    (3, 2, 3, '', 'MATH221'),   -- Statistics with Probability
    (3, 2, 3, '', 'ECON100'),   -- Principles of Economics
    (3, 2, 3, '', 'CS213'),     -- Object-Oriented Programming
    (3, 2, 3, '', 'CS221');     -- Discrete Structures and Theory

-- Year 2 Semester 4 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 2, 4, 'I', 'MATH223'),   -- Quantitative Methods
    (3, 2, 4, 'I', 'SOAN311'),   -- Leadership Seminar 3: The Economic Development of a Good Society
    (3, 2, 4, 'I', 'CS222'),     -- Data Structures and Algorithms
    (3, 2, 4, 'I', 'CS323'),     -- Database Systems
    (3, 2, 4, 'I', 'CS254');     -- Introduction to Artificial Intelligence

-- Year 2 Semester 4 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 2, 4, 'II', 'MATH223'),    -- Quantitative Methods
    (3, 2, 4, 'II', 'SOAN311'),    -- Leadership Seminar 3: The Economic Development of a Good Society
    (3, 2, 4, 'II', 'ELECTIVE2'),  -- Non-Major Elective
    (3, 2, 4, 'II', 'CS323'),      -- Database Systems
    (3, 2, 4, 'II', 'CS254');      -- Introduction to Artificial Intelligence

-- Year 3 Semester 5 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 3, 5, 'I', 'SOAN411'),    -- Leadership Seminar 4 for Engineers: Leadership as Service
    (3, 3, 5, 'I', 'CS341'),      -- Web Development (Elective)
    (3, 3, 5, 'I', 'IS351'),      -- Systems Analysis and Design
    (3, 3, 5, 'I', 'BUSA224');    -- Finance for Non-Finance

-- Year 3 Semester 5 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 3, 5, 'II', 'ELECTIVE1'),  -- Major Elective (4 credits)
    (3, 3, 5, 'II', 'CS341'),      -- Web Development (Elective)
    (3, 3, 5, 'II', 'IS351'),      -- Systems Analysis and Design
    (3, 3, 5, 'II', 'BUSA224');    -- Finance for Non-Finance

-- Year 3 Semester 6 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 3, 6, 'I', 'SOAN411'),    -- Leadership Seminar 4 for Engineers: Leadership as Service
    (3, 3, 6, 'I', 'CS415'),      -- Software Engineering
    (3, 3, 6, 'I', 'CS331'),      -- Computer Architecture
    (3, 3, 6, 'I', 'SOAN325'),    -- Research Methods
    (3, 3, 6, 'I', 'CS361');      -- Introduction to Modelling and Simulation

-- Year 3 Semester 6 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 3, 6, 'II', 'ELECTIVE1'),  -- Major Elective (4 credits)
    (3, 3, 6, 'II', 'CS415'),      -- Software Engineering
    (3, 3, 6, 'II', 'CS331'),      -- Computer Architecture
    (3, 3, 6, 'II', 'SOAN325'),    -- Research Methods
    (3, 3, 6, 'II', 'CS361');      -- Introduction to Modelling and Simulation

-- Year 4 Semester 7 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 7, 'I', 'CS442'),       -- E-Commerce (Elective)
    (3, 4, 7, 'I', 'IS451'),       -- Information and Systems Security (Elective)
    (3, 4, 7, 'I', 'ELECTIVE'),   -- Elective (4 credits)
    (3, 4, 7, 'I', 'BUSA491');   -- Thesis 1

-- Year 4 Semester 7 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 7, 'II', 'CS442'),       -- E-Commerce (Elective)
    (3, 4, 7, 'II', 'IS451'),       -- Information and Systems Security (Elective)
    (3, 4, 7, 'II', 'ELECTIVE'),   -- Elective (4 credits)
    (3, 4, 7, 'II', 'BUSA401_A');   -- Entrepreneurship I (Capstone)

-- Year 4 Semester 7 - Type III
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 7, 'III', 'CS442'),       -- E-Commerce (Elective)
    (3, 4, 7, 'III', 'IS451'),       -- Information and Systems Security (Elective)
    (3, 4, 7, 'III', 'ELECTIVE'),   -- Elective (4 credits)
    (3, 4, 7, 'III', 'ELECTIVE1');   -- Extra Major Elective




-- Year 4 Semester 8 - Type I
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 8, 'I', 'CS432'),         -- Computer Networks and Data Communications
    (3, 4, 8, 'I', 'ELECTIVE'),     -- Elective (4 credits)
    (3, 4, 8, 'I', 'ELECTIVE'),     -- Elective (4 credits)
    (3, 4, 8, 'I', 'CS400_B');       -- Thesis II

-- Year 4 Semester 8 - Type II
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 8, 'II', 'CS432'),         -- Computer Networks and Data Communications
    (3, 4, 8, 'II', 'ELECTIVE'),     -- Elective (4 credits)
    (3, 4, 8, 'II', 'ELECTIVE');     -- Elective (4 credits)
    

-- Year 4 Semester 8 - Type III
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (3, 4, 8, 'III', 'CS432'),        -- Computer Networks and Data Communications
    (3, 4, 8, 'III', 'ELECTIVE'),    -- Elective (4 credits)
    (3, 4, 8, 'III', 'ELECTIVE'),    -- Elective (4 credits)
    (3, 4, 8, 'III', 'BUSA401_B');    -- Entrepreneurship II (Capstone)


--COMPUTER ENGINEERING

-- ----------------------------------------------------
-- Insert Correct ProgramPlan Entries for Computer Engineering (MajorID = 4)
-- ----------------------------------------------------

-- Year 1, Semester 1 - Core Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 1, 1, '', 'AS111'),      -- Ashesi Success
    (4, 1, 1, '', 'ENGL112'),    -- Written and Oral Communication
    (4, 1, 1, '', 'BUSA161'),    -- Foundations of Design and Entrepreneurship I
    (4, 1, 1, '', 'ENGR112'),    -- Introduction to Engineering
    (4, 1, 1, '', 'MATH161');    -- Engineering Calculus

-- Year 1, Semester 2 - Core Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 1, 2, '', 'CS112'),      -- Computer Programming for Engineering
    (4, 1, 2, '', 'MATH211'),    -- Multivariable Calculus and Linear Algebra
    (4, 1, 2, '', 'BUSA162'),    -- Foundations of Design and Entrepreneurship II
    (4, 1, 2, '', 'ME101'),      -- Introduction to Mechanics
    (4, 1, 2, '', 'SOAN111');    -- Leadership Seminar 1: What Makes a Good Leader?

-- Year 2, Semester 3 - Core Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 2, 3, '', 'SC113'),      -- Physics II: Electromagnetism
    (4, 2, 3, '', 'MATH152'),    -- Statistics for Engineering and Economics
    (4, 2, 3, '', 'CS221'),      -- Discrete Structures and Theory
    (4, 2, 3, '', 'CS213'),      -- Object-Oriented Programming
    (4, 2, 3, '', 'SOAN211');    -- Leadership Seminar 2: Rights, Ethics, and Rule of Law

-- Year 2, Semester 4 - Core Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 2, 4, '', 'MATH251'),    -- Differential Equations & Numerical Methods
    (4, 2, 4, '', 'SOAN311'),    -- Leadership Seminar 3: The Economic Development of a Good Society
    (4, 2, 4, '', 'EE222'),      -- Circuits and Electronics
    (4, 2, 4, '', 'SC221'),      -- Materials Science & Chemistry
    (4, 2, 4, '', 'ENGL113'),    -- Text & Meaning
    (4, 2, 4, '', 'CE122');      -- Applied Programming for Engineers

-- Year 3, Semester 5 - Core Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 3, 5, '', 'CS331'),      -- Computer Architecture
    (4, 3, 5, '', 'ENGR311'),    -- System Dynamics
    (4, 3, 5, '', 'SOAN411'),    -- Leadership Seminar 4 for Engineers: Leadership as Service
    (4, 3, 5, '', 'ENGR212'),    -- Instrumentation for Engineering
    (4, 3, 5, '', 'ENGR300'),    -- Third Year Group Project & Seminar
    (4, 3, 5, '', 'EE320');      -- Signals & Systems

-- Year 3, Semester 6 - Core and Elective Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 3, 6, '', 'ENGR312'),           -- Control Systems
    (4, 3, 6, '', 'CS432'),             -- Networks and Distributed Computing
    (4, 3, 6, '', 'CS222'),             -- Data Structures and Algorithms
    (4, 3, 6, '', 'CE322'),             -- Digital Systems Design
    (4, 3, 6, '', 'ELECTIVE1');         -- Elective (4 credits)

-- Year 4, Semester 7 - Core and Elective Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 4, 7, '', 'CS433'),            -- Operating Systems and Systems Administration
    (4, 4, 7, '', 'ELECTIVE1'),        -- CE Elective (4 credits)
    (4, 4, 7, '', 'ECON100'),          -- Principles of Economics
    (4, 4, 7, '', 'CE451'),            -- Embedded Systems
    (4, 4, 7, '', 'ELECTIVE');        -- Elective (4 credits)

-- Year 4, Semester 8 - Core and Elective Courses
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (4, 4, 8, '', 'ENGR413'),           -- Project Management & Professional Practice
    (4, 4, 8, '', 'ELECTIVE1'),         -- CE Elective
    (4, 4, 8, '', 'ELECTIVE2'),         -- African Studies Elective
    (4, 4, 8, '', 'ENGR401');           -- Senior Project and Seminar


--MECHANICAL ENGINEERING

-- Year 1
-- Semester 1
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 1, 1, '', 'AS111'),        -- Ashesi Success
    (6, 1, 1, '', 'ENGL112'),      -- Written and Oral Communication
    (6, 1, 1, '', 'BUSA161'),      -- Foundations of Design and Entrepreneurship I
    (6, 1, 1, '', 'ENGR112'),      -- Introduction to Engineering
    (6, 1, 1, '', 'MATH161');      -- Engineering Calculus

-- Semester 2
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 1, 2, '', 'CS112'),        -- Computer Programming for Engineering
    (6, 1, 2, '', 'MATH211'),      -- Multivariable Calculus and Linear Algebra
    (6, 1, 2, '', 'BUSA162'),      -- Foundations of Design and Entrepreneurship II
    (6, 1, 2, '', 'ME101'),        -- Introduction to Mechanics
    (6, 1, 2, '', 'SOAN111');      -- Leadership Seminar 1: What Makes a Good Leader?

-- Year 2
-- Semester 3
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 2, 3, '', 'SC113'),        -- Physics II: Electromagnetism
    (6, 2, 3, '', 'ME201'),        -- Thermodynamics
    (6, 2, 3, '', 'MATH152'),      -- Statistics for Engineering and Economics
    (6, 2, 3, '', 'SOAN211'),      -- Leadership Seminar 2: Rights, Ethics, and Rule of Law
    (6, 2, 3, '', 'ME442');        -- Computer Aided Design (CAD) / Manufacturing (CAM)

-- Semester 4
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 2, 4, '', 'MATH251'),      -- Differential Equations & Numerical Methods
    (6, 2, 4, '', 'SOAN311'),      -- Leadership Seminar 3: The Economic Development of a Good Society
    (6, 2, 4, '', 'EE222'),        -- Circuits and Electronics
    (6, 2, 4, '', 'SC221'),        -- Materials Science & Chemistry
    (6, 2, 4, '', 'ENGL113'),      -- Text & Meaning
    (6, 2, 4, '', 'CE122');        -- Applied Programming for Engineers

-- Year 3
-- Semester 5
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 3, 5, '', 'EE341'),        -- AC Electrical Machines
    (6, 3, 5, '', 'ENGR311'),      -- System Dynamics
    (6, 3, 5, '', 'SOAN411'),      -- Leadership Seminar 4 for Engineers: Leadership as Service
    (6, 3, 5, '', 'ENGR212'),      -- Instrumentation for Engineering
    (6, 3, 5, '', 'ENGR300'),      -- Third Year Group Project & Seminar
    (6, 3, 5, '', 'EE320');        -- Signals & Systems

-- Semester 6
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 3, 6, '', 'ENGR312'),      -- Control Systems
    (6, 3, 6, '', 'ME301'),        -- Mechanical Machine Design
    (6, 3, 6, '', 'ME431'),        -- Fluid Mechanics
    (6, 3, 6, '', 'ME441'),        -- Manufacturing Processes
    (6, 3, 6, '', 'ELECTIVE1');    -- ME Elective

-- Year 4
-- Semester 7
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 4, 7, '', 'ME311'),        -- Mechanics of Materials/Structural Engineering
    (6, 4, 7, '', 'ME422'),        -- Heat and Mass Transfer
    (6, 4, 7, '', 'ECON100'),      -- Principles of Economics
    (6, 4, 7, '', 'ELECTIVE'),        
    (6, 4, 7, '', 'ELECTIVE1');    -- Elective (4 credits)

-- Semester 8
-- No Type Specified
INSERT INTO ProgramPlan (MajorID, YearNumber, SemesterNumber, SubType, CourseCode)
VALUES
    (6, 4, 8, '', 'ENGR413'),      -- Project Management & Professional Practice
    (6, 4, 8, '', 'ELECTIVE1'),    -- ME Elective
    (6, 4, 8, '', 'ELECTIVE2'),    -- African Studies Elective
    (6, 4, 8, '', 'ENGR401');      -- Senior Project and Seminar (Capstone)

CREATE TABLE IF NOT EXISTS UpdatedSessionSchedule LIKE SessionSchedule;

CREATE TABLE SessionLocationPreferences (
    PreferenceID INT PRIMARY KEY AUTO_INCREMENT,
    CourseCode VARCHAR(255) NOT NULL,
    CourseName VARCHAR(255) NOT NULL,
    Location VARCHAR(255) NOT NULL,
    SessionType VARCHAR(50) NOT NULL,
    UNIQUE (CourseCode, Location, SessionType)
) ENGINE=InnoDB;

-- Insert statements for SessionLocationPreferences
INSERT INTO SessionLocationPreferences (CourseCode, CourseName, Location, SessionType)
VALUES ('AS111', 'Ashesi Success', 'Jackson Lab 221', 'Seminar'),
       ('AS111', 'Ashesi Success', 'Jackson Lab 222', 'Seminar'),
       ('AS111', 'Ashesi Success', 'Apt Hall 216', 'Seminar'),
       ('AS111', 'Ashesi Success', 'Nutor Hall 216', 'Seminar'),
       ('AS111', 'Ashesi Success', 'Bio Lab', 'Seminar'),
       ('AS111', 'Ashesi Success', 'Science Lab', 'Seminar'),
       ('AS111', 'Ashesi Success', 'Norton-Motulsky 207A', 'Seminar'),
       ('AS111', 'Ashesi Success', 'Fab Lab 103', 'Seminar'),
       ('AS111', 'Ashesi Success', 'Fab Lab 203', 'Seminar'),
       ('AS111', 'Ashesi Success', 'Fab Lab 303', 'Seminar'),
       ('AS111', 'Ashesi Success', 'Nutor Hall 115', 'Seminar'),
       ('BUSA432', 'Organisational Development', 'Radichel MPR', 'Lecture'),
       ('BUSA432', 'Organisational Development', 'Radichel MPR', 'Discussion'),
       ('BUSA432', 'Organisational Development', 'Apt Hall 216', 'Lecture'),
       ('BUSA432', 'Organisational Development', 'Jackson Hall 115', 'Discussion'),
       ('BUSA132', 'Organizational Behaviour', 'Jackson Lab 221', 'Lecture'),
       ('BUSA132', 'Organizational Behaviour', 'Nutor Hall 100', 'Discussion'),
       ('BUSA132', 'Organizational Behaviour', 'Jackson Hall 115', 'Lecture'),
       ('BUSA161', 'Foundations of Design and Entrepreneurship I', 'Nutor Hall 115', 'Lecture'),
       ('BUSA161', 'Foundations of Design and Entrepreneurship I', 'Nutor Hall 115', 'Discussion'),
       ('BUSA161', 'Foundations of Design and Entrepreneurship I', 'Norton-Motulsky 207B', 'Lecture'),
       ('BUSA161', 'Foundations of Design and Entrepreneurship I', 'Norton-Motulsky 207B', 'Discussion'),
       ('BUSA161', 'Foundations of Design and Entrepreneurship I', 'Fab Lab 303', 'Lecture'),
       ('BUSA161', 'Foundations of Design and Entrepreneurship I', 'Nutor Hall 216', 'Discussion'),
       ('BUSA161', 'Foundations of Design and Entrepreneurship I', 'Fab Lab 203', 'Lecture'),
       ('BUSA161', 'Foundations of Design and Entrepreneurship I', 'Fab Lab 203', 'Discussion'),
       ('BUSA161', 'Foundations of Design and Entrepreneurship I', 'Nutor Hall 216', 'Lecture'),
       ('BUSA162', 'Foundations of Design and Entrepreneurship II', 'Nutor Hall 115', 'Lecture'),
       ('BUSA162', 'Foundations of Design and Entrepreneurship II', 'Nutor Hall 115', 'Discussion'),
       ('BUSA162', 'Foundations of Design and Entrepreneurship II', 'Norton-Motulsky 207A', 'Lecture'),
       ('BUSA162', 'Foundations of Design and Entrepreneurship II', 'Norton-Motulsky 207A', 'Discussion'),
       ('BUSA162', 'Foundations of Design and Entrepreneurship II', 'Norton-Motulsky 207B', 'Lecture'),
       ('BUSA162', 'Foundations of Design and Entrepreneurship II', 'Nutor Hall 216', 'Discussion'),
       ('BUSA162', 'Foundations of Design and Entrepreneurship II', 'Norton-Motulsky 207B', 'Discussion'),
       ('BUSA210', 'Financial Accounting', 'Apt Hall 217', 'Lecture'),
       ('BUSA210', 'Financial Accounting', 'Radichel MPR', 'Discussion'),
       ('BUSA210', 'Financial Accounting', 'Norton-Motulsky 207B', 'Lecture'),
       ('BUSA210', 'Financial Accounting', 'Jackson Hall 116', 'Lecture'),
       ('BUSA210', 'Financial Accounting', 'Radichel MPR', 'Lecture'),
       ('BUSA220', 'Introduction to Finance', 'Jackson Hall 115', 'Lecture'),
       ('BUSA220', 'Introduction to Finance', 'Radichel MPR', 'Discussion'),
       ('BUSA220', 'Introduction to Finance', 'Nutor Hall 216', 'Lecture'),
       ('BUSA224', 'Finance for Non-finance Managers', 'Norton-Motulsky 207B', 'Lecture'),
       ('BUSA224', 'Finance for Non-finance Managers', 'Norton-Motulsky 207B', 'Discussion'),
       ('BUSA224', 'Finance for Non-finance Managers', 'Nutor Hall 216', 'Lecture'),
       ('BUSA224', 'Finance for Non-finance Managers', 'D-Lab 102', 'Discussion'),
       ('BUSA224', 'Finance for Non-finance Managers', 'Apt Hall 216', 'Discussion'),
       ('BUSA304', 'Operations Management', 'Nutor Hall 216', 'Lecture'),
       ('BUSA304', 'Operations Management', 'Nutor Hall 216', 'Discussion'),
       ('BUSA304', 'Operations Management', 'Norton-Motulsky 207B', 'Lecture'),
       ('BUSA304', 'Operations Management', 'Nutor Hall 115', 'Discussion'),
       ('BUSA304', 'Operations Management', 'Radichel MPR', 'Lecture'),
       ('BUSA304', 'Operations Management', 'Radichel MPR', 'Discussion'),
       ('BUSA311', 'Managerial Accounting', 'Radichel MPR', 'Lecture'),
       ('BUSA311', 'Managerial Accounting', 'Nutor Hall 216', 'Discussion'),
       ('BUSA311', 'Managerial Accounting', 'Nutor Hall 100', 'Lecture'),
       ('BUSA311', 'Managerial Accounting', 'Norton-Motulsky 207A', 'Discussion'),
       ('BUSA321', 'Investments', 'Norton-Motulsky 207B', 'Lecture'),
       ('BUSA321', 'Investments', 'Jackson Hall 116', 'Discussion'),
       ('BUSA323', 'Corporate Finance', 'Nutor Hall 216', 'Lecture'),
       ('BUSA323', 'Corporate Finance', 'Nutor Hall 216', 'Discussion'),
       ('BUSA323', 'Corporate Finance', 'Nutor Hall 115', 'Lecture'),
       ('BUSA323', 'Corporate Finance', 'Jackson Hall 115', 'Discussion');

-- Continuing insert statements for SessionLocationPreferences
INSERT INTO SessionLocationPreferences (CourseCode, CourseName, Location, SessionType)
VALUES 
       ('BUSA332', 'Organisational Behavior', 'Norton-Motulsky 207B', 'Lecture'),
       ('BUSA332', 'Organisational Behavior', 'Radichel MPR', 'Discussion'),
       ('BUSA332', 'Organisational Behavior', 'Jackson Lab 221', 'Discussion'),
       ('BUSA341', 'Marketing', 'Norton-Motulsky 207B', 'Lecture'),
       ('BUSA341', 'Marketing', 'Databank Foundation Hall 218', 'Discussion'),
       ('BUSA350', 'International Trade and Policy', 'Radichel MPR', 'Lecture'),
       ('BUSA350', 'International Trade and Policy', 'Norton-Motulsky 207B', 'Discussion'),
       ('BUSA350', 'International Trade and Policy', 'Apt Hall 216', 'Lecture'),
       ('BUSA350', 'International Trade and Policy', 'Nutor Hall 216', 'Discussion'),
       ('BUSA401_A', 'Entrepreneurship I', 'Nutor Hall 115', 'Discussion'),
       ('BUSA401_A', 'Entrepreneurship I', 'Nutor Hall 115', 'Lecture'),
       ('BUSA401_B', 'Entrepreneurship II', 'Nutor Hall 115', 'Seminar'),
       ('BUSA401_B', 'Entrepreneurship II', 'Norton-Motulsky 207A', 'Lecture'),
       ('BUSA402', 'Business Law', 'Nutor Hall 115', 'Lecture'),
       ('BUSA402', 'Business Law', 'Nutor Hall 100', 'Discussion'),
       ('BUSA402', 'Business Law', 'Norton-Motulsky 207A', 'Lecture'),
       ('BUSA402', 'Business Law', 'Norton-Motulsky 207A', 'Discussion'),
       ('BUSA402', 'Business Law', 'Radichel MPR', 'Lecture'),
       ('BUSA402', 'Business Law', 'Norton-Motulsky 207B', 'Discussion'),
       ('BUSA405', 'Competitive Strategy', 'Norton-Motulsky 207A', 'Discussion'),
       ('BUSA405', 'Competitive Strategy', 'Apt Hall 216', 'Lecture'),
       ('BUSA405', 'Competitive Strategy', 'Jackson Lab 221', 'Discussion'),
       ('BUSA411', 'Applied Project I (BA)', 'Jackson Hall 116', 'Seminar'),
       ('BUSA411', 'Applied Project I (BA)', 'Norton-Motulsky 207A', 'Seminar'),
       ('BUSA412', 'Applied Project II (BA)', 'Apt Hall 216', 'Seminar'),
       ('BUSA422', 'Corporate Finance', 'Nutor Hall 115', 'Lecture'),
       ('BUSA422', 'Corporate Finance', 'Nutor Hall 115', 'Discussion'),
       ('BUSA422', 'Corporate Finance', 'Nutor Hall 216', 'Lecture'),
       ('BUSA422', 'Corporate Finance', 'Nutor Hall 216', 'Discussion'),
       ('BUSA422', 'Corporate Finance', 'Norton-Motulsky 207B', 'Lecture'),
       ('BUSA422', 'Corporate Finance', 'Norton-Motulsky 207B', 'Discussion'),
       ('BUSA423', 'International Finance', 'Norton-Motulsky 207B', 'Lecture'),
       ('BUSA423', 'International Finance', 'Nutor Hall 100', 'Discussion'),
       ('BUSA423', 'International Finance', 'Norton-Motulsky 207A', 'Lecture'),
       ('BUSA423', 'International Finance', 'Jackson Hall 116', 'Discussion'),
       ('BUSA425', 'Venture Capital Investment', 'Nutor Hall 216', 'Lecture'),
       ('BUSA425', 'Venture Capital Investment', 'Apt Hall 217', 'Discussion'),
       ('BUSA430', 'Human Resource Management', 'Norton-Motulsky 207B', 'Lecture'),
       ('BUSA430', 'Human Resource Management', 'Nutor Hall 216', 'Discussion'),
       ('BUSA431', 'Real Estate Development', 'Databank Foundation Hall 218', 'Lecture'),
       ('BUSA431', 'Real Estate Development', 'Databank Foundation Hall 218', 'Discussion'),
       ('BUSA431', 'Real Estate Development', 'Apt Hall 216', 'Lecture'),
       ('BUSA431', 'Real Estate Development', 'Norton-Motulsky 207A', 'Discussion'),
       ('BUSA433', 'AI in Business: Empowering Tomorrow''s Leaders', 'Radichel MPR', 'Lecture'),
       ('BUSA433', 'AI in Business: Empowering Tomorrow''s Leaders', 'Radichel MPR', 'Discussion'),
       ('BUSA442', 'Strategic Brand Management', 'Jackson Hall 116', 'Lecture'),
       ('BUSA442', 'Strategic Brand Management', 'Nutor Hall 115', 'Discussion'),
       ('BUSA442', 'Strategic Brand Management', 'Radichel MPR', 'Lecture'),
       ('BUSA442', 'Strategic Brand Management', 'Jackson Lab 222', 'Discussion'),
       ('BUSA444', 'Supply Chain Management', 'Nutor Hall 216', 'Lecture'),
       ('BUSA444', 'Supply Chain Management', 'Jackson Hall 116', 'Discussion'),
       ('BUSA444', 'Supply Chain Management', 'Nutor Hall 100', 'Lecture'),
       ('BUSA444', 'Supply Chain Management', 'Jackson Lab 222', 'Discussion'),
       ('BUSA446', 'Integrated Marketing Communications', 'Jackson Lab 221', 'Discussion'),
       ('BUSA446', 'Integrated Marketing Communications', 'Apt Hall 217', 'Lecture'),
       ('BUSA451', 'Development Economics', 'D-Lab 102', 'Lecture'),
       ('BUSA451', 'Development Economics', 'Jackson Hall 115', 'Discussion'),
       ('BUSA455', 'Project Management', 'Norton-Motulsky 207B', 'Lecture'),
       ('BUSA455', 'Project Management', 'Apt Hall 217', 'Discussion'),
       ('BUSA456', 'Managerial Economics', 'Nutor Hall 216', 'Lecture'),
       ('BUSA456', 'Managerial Economics', 'Jackson Lab 221', 'Discussion'),
       ('BUSA457', 'Anti-Money Laundering', 'Norton-Motulsky 207A', 'Lecture'),
       ('BUSA457', 'Anti-Money Laundering', 'Norton-Motulsky 207A', 'Discussion'),
       ('BUSA458', 'Data Analytics for Business', 'Apt Hall 217', 'Lecture'),
       ('BUSA458', 'Data Analytics for Business', 'Science Lab', 'Discussion'),
       ('BUSA462', 'New Product Development', 'Nutor Hall 100', 'Discussion'),
       ('BUSA462', 'New Product Development', 'Apt Hall 216', 'Lecture'),
       ('BUSA491', 'Undergraduate Thesis I (BA)', 'Nutor Hall 216', 'Seminar'),
       ('BUSA491', 'Undergraduate Thesis I (BA)', 'Nutor Hall 115', 'Seminar'),
       ('BUSA492', 'Undergraduate Thesis II (BA)', 'Nutor Hall 100', 'Seminar');

INSERT INTO SessionLocationPreferences (CourseCode, CourseName, Location, SessionType)
VALUES 
       ('CE122', 'Applied Programming for Engineers', 'Fab Lab 303', 'Lecture'),
       ('CE122', 'Applied Programming for Engineers', 'Fab Lab 303', 'Lab'),
       ('CE322', 'Digital Systems Design', 'Fab Lab 303', 'Lab'),
       ('CE322', 'Digital Systems Design', 'Fab Lab 203', 'Lecture'),
       ('CE451', 'Embedded Systems', 'Fab Lab 203', 'Lab'),
       ('CE451', 'Embedded Systems', 'Fab Lab 203', 'Lecture'),
       ('CE451', 'Embedded Systems', 'Fab Lab 303', 'Lab'),
       ('CS452', 'Machine Learning', 'Fab Lab 203', 'Lecture'),
       ('CS452', 'Machine Learning', 'Fab Lab 203', 'Lab'),
       ('CS452', 'Machine Learning', 'D-Lab 102', 'Lecture'),
       ('CS452', 'Machine Learning', 'D-Lab 102', 'Lab'),
       ('CS111', 'Introduction to Computing and Information Systems', 'Jackson Lab 222', 'Lecture'),
       ('CS111', 'Introduction to Computing and Information Systems', 'Jackson Lab 222', 'Lab'),
       ('CS111', 'Introduction to Computing and Information Systems', 'Jackson Lab 221', 'Lecture'),
       ('CS111', 'Introduction to Computing and Information Systems', 'Jackson Lab 221', 'Lab'),
       ('CS111', 'Introduction to Computing and Information Systems', 'D-Lab 102', 'Lecture'),
       ('CS111', 'Introduction to Computing and Information Systems', 'Fab Lab 303', 'Lab'),
       ('CS112', 'Computer Programming for Engineering', 'Fab Lab 203', 'Lecture'),
       ('CS112', 'Computer Programming for Engineering', 'Fab Lab 203', 'Lab'),
       ('CS212', 'Computer Programming for CS', 'Jackson Lab 221', 'Lecture'),
       ('CS212', 'Computer Programming for CS', 'Jackson Lab 222', 'Discussion'),
       ('CS212', 'Computer Programming for CS', 'Apt Hall 216', 'Lecture'),
       ('CS212', 'Computer Programming for CS', 'Jackson Lab 221', 'Lab'),
       ('CS212', 'Computer Programming for CS', 'Apt Hall 216', 'Period'),
       ('CS213', 'Object-Oriented Programming', 'Apt Hall 217', 'Lecture'),
       ('CS213', 'Object-Oriented Programming', 'Apt Hall 217', 'Lab'),
       ('CS213', 'Object-Oriented Programming', 'Nutor Hall 100', 'Lab'),
       ('CS213', 'Object-Oriented Programming', 'Nutor Hall 216', 'Lecture'),
       ('CS213', 'Object-Oriented Programming', 'Jackson Lab 222', 'Lab'),
       ('CS221', 'Discrete Structures and Theory', 'Databank Foundation Hall 218', 'Lecture'),
       ('CS221', 'Discrete Structures and Theory', 'Databank Foundation Hall 218', 'Lab'),
       ('CS222', 'Data Structures and Algorithms', 'Apt Hall 216', 'Lecture'),
       ('CS222', 'Data Structures and Algorithms', 'Databank Foundation Hall 218', 'Lab'),
       ('CS254', 'Introduction to Artificial Intelligence', 'Apt Hall 217', 'Lab'),
       ('CS254', 'Introduction to Artificial Intelligence', 'Apt Hall 217', 'Lecture'),
       ('CS313', 'Intermediate Computer Programming', 'Jackson Hall 115', 'Lecture'),
       ('CS313', 'Intermediate Computer Programming', 'Jackson Hall 115', 'Lab'),
       ('CS313', 'Intermediate Computer Programming', 'Jackson Hall 116', 'Lecture'),
       ('CS313', 'Intermediate Computer Programming', 'Jackson Hall 116', 'Lab'),
       ('CS323', 'Database Management / Database Systems', 'Nutor Hall 100', 'Lecture'),
       ('CS323', 'Database Management / Database Systems', 'Nutor Hall 100', 'Lab'),
       ('CS330', 'Hardware and Systems Fundamentals', 'Jackson Hall 115', 'Lecture'),
       ('CS330', 'Hardware and Systems Fundamentals', 'Jackson Hall 115', 'Lab'),
       ('CS330', 'Hardware and Systems Fundamentals', 'Nutor Hall 216', 'Lecture'),
       ('CS330', 'Hardware and Systems Fundamentals', 'Nutor Hall 216', 'Lab'),
       ('CS331', 'Computer Organization and Architecture', 'D-Lab 102', 'Lecture'),
       ('CS331', 'Computer Organization and Architecture', 'Science Lab', 'Lab'),
       ('CS331', 'Computer Organization and Architecture', 'Bio Lab', 'Lab'),
       ('CS331', 'Computer Organization and Architecture', 'Bio Lab', 'Lecture'),
       ('CS331', 'Computer Organization and Architecture', 'D-Lab 102', 'Lab'),
       ('CS341', 'Web Technologies', 'Jackson Lab 221', 'Lecture'),
       ('CS341', 'Web Technologies', 'Jackson Lab 221', 'Lab'),
       ('CS341', 'Web Technologies', 'Jackson Hall 115', 'Lecture'),
       ('CS341', 'Web Technologies', 'D-Lab 102', 'Lecture'),
       ('CS341', 'Web Technologies', 'Databank Foundation Hall 218', 'Lab'),
       ('CS341-LAB', 'Web Technologies-LAB', 'Apt Hall 216', 'Lab'),
       ('CS353', 'Introduction to AI Robotics', 'Apt Hall 217', 'Lecture'),
       ('CS353', 'Introduction to AI Robotics', 'Jackson Lab 222', 'Lab'),
       ('CS361', 'Introduction to Modelling & Simulation', 'Jackson Lab 222', 'Lecture'),
       ('CS361', 'Introduction to Modelling & Simulation', 'Jackson Lab 222', 'Lab'),
       ('CS410', 'CSIS Capstone Seminar', 'Nutor Hall 100', 'Seminar'),
       ('CS410', 'CSIS Capstone Seminar', 'Nutor Hall 100', 'Set up for grading only'),
       ('CS413', 'Concepts of Programming Languages', 'Jackson Lab 221', 'Lecture'),
       ('CS413', 'Concepts of Programming Languages', 'Jackson Hall 116', 'Discussion'),
       ('CS415', 'Software Engineering', 'Jackson Lab 222', 'Lab'),
       ('CS415', 'Software Engineering', 'Jackson Lab 222', 'Lecture'),
       ('CS415', 'Software Engineering', 'Jackson Lab 222', 'Period'),
       ('CS415', 'Software Engineering', 'Jackson Lab 222', 'Discussion'),
       ('CS424', 'Advanced Database Systems', 'D-Lab 102', 'Lecture'),
       ('CS424', 'Advanced Database Systems', 'Apt Hall 216', 'Lab'),
       ('CS432', 'Networks and Data Communication', 'Nutor Hall 216', 'Lecture'),
       ('CS432', 'Networks and Data Communication', 'Apt Hall 216', 'Lab'),
       ('CS433', 'Operating Systems / Systems Administration', 'Norton-Motulsky 207A', 'Lecture'),
       ('CS433', 'Operating Systems / Systems Administration', 'D-Lab 102', 'Lab'),
       ('CS433', 'Operating Systems / Systems Administration', 'D-Lab 102', 'Lecture'),
       ('CS442', 'E-Commerce', 'Jackson Lab 222', 'Lecture'),
       ('CS442', 'E-Commerce', 'Jackson Lab 222', 'Lab'),
       ('CS442', 'E-Commerce', 'Jackson Lab 221', 'Lecture'),
       ('CS442', 'E-Commerce', 'Fab Lab 303', 'Lab'),
       ('CS443', 'Mobile Web Programming / Mobile App Dev', 'Jackson Lab 221', 'Lecture'),
       ('CS443', 'Mobile Web Programming / Mobile App Dev', 'Jackson Lab 221', 'Lab'),
       ('CS451', 'Computer Graphics', 'D-Lab 102', 'Lecture'),
       ('CS451', 'Computer Graphics', 'D-Lab 102', 'Lab'),
       ('CS456', 'Algorithm Design and Analysis', 'Nutor Hall 100', 'Lecture'),
       ('CS456', 'Algorithm Design and Analysis', 'Nutor Hall 115', 'Lab'),
       ('CS456', 'Algorithm Design and Analysis', 'Nutor Hall 216', 'Lab'),
       ('CS456', 'Algorithm Design and Analysis', 'Jackson Hall 115', 'Lecture');

-- Continuing insert statements for SessionLocationPreferences
INSERT INTO SessionLocationPreferences (CourseCode, CourseName, Location, SessionType)
VALUES 
       ('CS458', 'Internet of Things', 'Fab Lab 203', 'Lecture'),
       ('CS458', 'Internet of Things', 'Fab Lab 303', 'Lab'),
       ('CS458', 'Internet of Things', 'Science Lab', 'Lecture'),
       ('CS461', 'Data Science', 'D-Lab 102', 'Lecture'),
       ('CS461', 'Data Science', 'Apt Hall 217', 'Lab'),
       ('CS462', 'Cloud Computing', 'Jackson Lab 221', 'Lecture'),
       ('CS462', 'Cloud Computing', 'D-Lab 102', 'Lab'),
       ('CS462', 'Cloud Computing', 'D-Lab 102', 'Lecture'),
       ('CS462', 'Cloud Computing', 'Science Lab', 'Lab'),
       ('CS464', 'Deep Learning', 'Jackson Lab 221', 'Lecture'),
       ('CS464', 'Deep Learning', 'Jackson Lab 222', 'Lab'),
       ('ECON100', 'Principles of Economics', 'Jackson Hall 115', 'Lecture'),
       ('ECON100', 'Principles of Economics', 'Jackson Hall 116', 'Discussion'),
       ('ECON100', 'Principles of Economics', 'Jackson Hall 116', 'Lecture'),
       ('ECON100', 'Principles of Economics', 'Jackson Hall 115', 'Discussion'),
       ('ECON100', 'Principles of Economics', 'Nutor Hall 100', 'Lecture'),
       ('ECON100', 'Principles of Economics', 'Nutor Hall 100', 'Discussion'),
       ('ECON100', 'Principles of Economics', 'Apt Hall 216', 'Discussion'),
       ('ECON100', 'Principles of Economics', 'Apt Hall 217', 'Lecture'),
       ('ECON101', 'Microeconomics', 'Apt Hall 217', 'Lecture'),
       ('ECON101', 'Microeconomics', 'Apt Hall 217', 'Discussion'),
       ('ECON101', 'Microeconomics', 'Jackson Hall 115', 'Lecture'),
       ('ECON201', 'Principles of Microeconomics', 'Jackson Lab 222', 'Lecture'),
       ('ECON201', 'Principles of Microeconomics', 'Norton-Motulsky 207A', 'Discussion'),
       ('ECON201', 'Principles of Microeconomics', 'Jackson Hall 115', 'Lecture'),
       ('ECON201', 'Principles of Microeconomics', 'Apt Hall 216', 'Discussion'),
       ('ECON201', 'Principles of Microeconomics', 'Apt Hall 216', 'Lecture'),
       ('ECON202', 'Principles of Macroeconomics', 'Databank Foundation Hall 218', 'Lecture'),
       ('ECON202', 'Principles of Macroeconomics', 'Databank Foundation Hall 218', 'Discussion'),
       ('ECON202', 'Principles of Macroeconomics', 'Apt Hall 217', 'Lecture'),
       ('ECON202', 'Principles of Macroeconomics', 'Radichel MPR', 'Discussion'),
       ('ECON231', 'Mathematics for Economists', 'Apt Hall 216', 'Lecture'),
       ('ECON231', 'Mathematics for Economists', 'Apt Hall 216', 'Discussion'),
       ('ECON231', 'Mathematics for Economists', 'Apt Hall 217', 'Lecture'),
       ('ECON231', 'Mathematics for Economists', 'Norton-Motulsky 207A', 'Discussion'),
       ('ECON301', 'Intermediate Microeconomic Theory I', 'Jackson Lab 221', 'Lecture'),
       ('ECON301', 'Intermediate Microeconomic Theory I', 'Norton-Motulsky 207A', 'Discussion'),
       ('ECON303', 'Intermediate Macroeconomic Theory I', 'Apt Hall 216', 'Lecture'),
       ('ECON303', 'Intermediate Macroeconomic Theory I', 'Apt Hall 216', 'Discussion'),
       ('ECON451', 'Development Economics', 'Nutor Hall 100', 'Lecture'),
       ('ECON451', 'Development Economics', 'Nutor Hall 100', 'Discussion'),
       ('EE422', 'Advanced Communication Systems', 'Science Lab', 'Lab'),
       ('EE422', 'Advanced Communication Systems', 'EE lab', 'Lecture'),
       ('EE422', 'Advanced Communication Systems', 'Bio Lab', 'Lecture'),
       ('EE222', 'Circuits and Electronics', 'EE lab', 'Lecture'),
       ('EE222', 'Circuits and Electronics', 'EE lab', 'Lab'),
       ('EE320', 'Signals & Systems', 'Fab Lab 203', 'Lab'),
       ('EE320', 'Signals & Systems', 'Fab Lab 203', 'Lecture'),
       ('EE320', 'Signals & Systems', 'Science Lab', 'Lecture'),
       ('EE320', 'Signals & Systems', 'EE lab', 'Lecture'),
       ('EE321', 'Communication Systems', 'Bio Lab', 'Lab'),
       ('EE321', 'Communication Systems', 'EE lab', 'Lecture'),
       ('EE321', 'Communication Systems', 'Bio Lab', 'Lecture'),
       ('EE341', 'AC Electrical Machines', 'EE lab', 'Lab'),
       ('EE341', 'AC Electrical Machines', 'EE lab', 'Lecture'),
       ('EE342', 'Electrical Machines and Power Electronics II', 'EE lab', 'Lab'),
       ('EE342', 'Electrical Machines and Power Electronics II', 'EE lab', 'Lecture'),
       ('EE342', 'Electrical Machines and Power Electronics II', 'Fab Lab 203', 'Lecture'),
       ('EE421', 'Digital and Analog Signal Processing in Telecommunications', 'Fab Lab 203', 'Lab'),
       ('EE421', 'Digital and Analog Signal Processing in Telecommunications', 'Fab Lab 203', 'Lecture'),
       ('EE421', 'Digital and Analog Signal Processing in Telecommunications', 'EE lab', 'Lab'),
       ('EE421', 'Digital and Analog Signal Processing in Telecommunications', 'Fab Lab 103', 'Lecture'),
       ('EE442', 'Power Electronics', 'EE lab', 'Lab'),
       ('EE442', 'Power Electronics', 'Science Lab', 'Lecture'),
       ('EE442', 'Power Electronics', 'Fab Lab 303', 'Lecture'),
       ('EE451', 'Power Engineering', 'EE lab', 'Lab'),
       ('EE451', 'Power Engineering', 'EE lab', 'Lecture'),
       ('EE453', 'Power Systems Analysis', 'EE lab', 'Lab'),
       ('EE453', 'Power Systems Analysis', 'EE lab', 'Lecture'),
       ('EE453', 'Power Systems Analysis', 'Science Lab', 'Lecture'),
       ('EE453', 'Power Systems Analysis', 'Fab Lab 303', 'Lecture'),
       ('EE454', 'Renewable Energy and Smart Grid', 'Bio Lab', 'Lab'),
       ('EE454', 'Renewable Energy and Smart Grid', 'Bio Lab', 'Lecture'),
       ('ENG232', 'African Folktales: How Stories Shape Us', 'Jackson Hall 116', 'Discussion'),
       ('ENG232', 'African Folktales: How Stories Shape Us', 'Radichel MPR', 'Lecture'),
       ('ENGL112', 'Written and Oral Communication', 'Jackson Hall 116', 'Lecture'),
       ('ENGL112', 'Written and Oral Communication', 'Jackson Lab 221', 'Discussion'),
       ('ENGL112', 'Written and Oral Communication', 'Jackson Lab 222', 'Lecture'),
       ('ENGL112', 'Written and Oral Communication', 'Jackson Lab 222', 'Discussion'),
       ('ENGL112', 'Written and Oral Communication', 'Apt Hall 216', 'Lecture'),
       ('ENGL112', 'Written and Oral Communication', 'Apt Hall 216', 'Discussion');

INSERT INTO SessionLocationPreferences (CourseCode, CourseName, Location, SessionType)
VALUES 
       ('ENGL112', 'Written and Oral Communication', 'Apt Hall 217', 'Discussion'),
       ('ENGL112', 'Written and Oral Communication', 'Nutor Hall 115', 'Lecture'),
       ('ENGL112', 'Written and Oral Communication', 'Norton-Motulsky 207A', 'Discussion'),
       ('ENGL112', 'Written and Oral Communication', 'Radichel MPR', 'Lecture'),
       ('ENGL112', 'Written and Oral Communication', 'Radichel MPR', 'Discussion'),
       ('ENGL112', 'Written and Oral Communication', 'Jackson Hall 115', 'Lecture'),
       ('ENGL112', 'Written and Oral Communication', 'Jackson Lab 221', 'Lecture'),
       ('ENGL112', 'Written and Oral Communication', 'Nutor Hall 115', 'Discussion'),
       ('ENGL112', 'Written and Oral Communication', 'D-Lab 102', 'Lecture'),
       ('ENGL112', 'Written and Oral Communication', 'Jackson Hall 115', 'Discussion'),
       ('ENGL113', 'Text and Meaning', 'Norton-Motulsky 207A', 'Lecture'),
       ('ENGL113', 'Text and Meaning', 'Norton-Motulsky 207A', 'Discussion'),
       ('ENGL113', 'Text and Meaning', 'Jackson Hall 116', 'Lecture'),
       ('ENGL113', 'Text and Meaning', 'Jackson Lab 221', 'Discussion'),
       ('ENGL113', 'Text and Meaning', 'Radichel MPR', 'Lecture'),
       ('ENGL113', 'Text and Meaning', 'Radichel MPR', 'Discussion'),
       ('ENGL113', 'Text and Meaning', 'D-Lab 102', 'Discussion'),
       ('ENGL113', 'Text and Meaning', 'Science Lab', 'Lecture'),
       ('ENGL113', 'Text and Meaning', 'Nutor Hall 115', 'Discussion'),
       ('ENGL113', 'Text and Meaning', 'Nutor Hall 216', 'Lecture'),
       ('ENGL113', 'Text and Meaning', 'EE lab', 'Discussion'),
       ('ENGR112', 'Introduction to Engineering', 'Fab Lab 203', 'Lab'),
       ('ENGR112', 'Introduction to Engineering', 'Fab Lab 203', 'Lecture'),
       ('ENGR112', 'Introduction to Engineering', 'Science Lab', 'Lecture'),
       ('ENGR212', 'Instrumentation for Engineering', 'Fab Lab 203', 'Lecture'),
       ('ENGR212-LAB', 'Instrumentation for Engineering - LAB', 'Fab Lab 203', 'Lab'),
       ('ENGR212-LAB', 'Instrumentation for Engineering - LAB', 'Fab Lab 103', 'Lab'),
       ('ENGR301', 'Year III Group Project and Seminar', 'EE lab', 'Seminar'),
       ('ENGR301', 'Year III Group Project and Seminar', 'EE lab', 'Lab'),
       ('ENGR301', 'Year III Group Project and Seminar', 'EE lab', 'Lecture'),
       ('ENGR311', 'System Dynamics', 'Fab Lab 303', 'Lab'),
       ('ENGR311', 'System Dynamics', 'Fab Lab 303', 'Lecture'),
       ('ENGR312', 'Control Systems', 'Fab Lab 303', 'Lab'),
       ('ENGR312', 'Control Systems', 'Fab Lab 303', 'Lecture'),
       ('ENGR401', 'Senior Project & Seminar', 'Databank Foundation Hall 218', 'Seminar'),
       ('ENGR401', 'Senior Project & Seminar', 'Fab Lab 303', 'Seminar'),
       ('ENGR401', 'Senior Project & Seminar', 'Nutor Hall 216', 'Seminar'),
       ('ENGR412', 'Synthetic Biological Engineering', 'Bio Lab', 'Lecture'),
       ('ENGR412', 'Synthetic Biological Engineering', 'Bio Lab', 'Lab'),
       ('ENGR413', 'Project Management and Professional Practice', 'Nutor Hall 216', 'Lecture'),
       ('ENGR413', 'Project Management and Professional Practice', 'Nutor Hall 216', 'Lab'),
       ('ENGR444', 'Automation and Production Systems', 'Bio Lab', 'Lab'),
       ('ENGR444', 'Automation and Production Systems', 'Fab Lab 203', 'Lecture'),
       ('ENGR444', 'Automation and Production Systems', 'Fab Lab 303', 'Lecture'),
       ('ENGR461', 'Financial Engineering', 'EE lab', 'Lecture'),
       ('ENGR461', 'Financial Engineering', 'Nutor Hall 100', 'Discussion'),
       ('FRENC111', 'Introductory French I', 'Jackson Lab 222', 'Lecture'),
       ('FRENC111', 'Introductory French I', 'Science Lab', 'Discussion'),
       ('IS333', 'IT Infrastructure and System Administration Lab', 'Jackson Lab 221', 'Lecture'),
       ('IS333', 'IT Infrastructure and System Administration Lab', 'D-Lab 102', 'Lab'),
       ('IS351', 'Systems Analysis and Design', 'Jackson Lab 222', 'Lecture'),
       ('IS351', 'Systems Analysis and Design', 'Jackson Lab 222', 'Lab'),
       ('IS351', 'Systems Analysis and Design', 'Nutor Hall 216', 'Lecture'),
       ('IS351', 'Systems Analysis and Design', 'Jackson Hall 116', 'Lab'),
       ('IS362', 'IS Project Management', 'Jackson Lab 221', 'Lecture'),
       ('IS362', 'IS Project Management', 'Jackson Lab 221', 'Lab'),
       ('IS451', 'Information and Systems Security', 'Apt Hall 216', 'Lecture'),
       ('IS451', 'Information and Systems Security', 'Nutor Hall 115', 'Lab'),
       ('IS451', 'Information and Systems Security', 'Nutor Hall 100', 'Lecture'),
       ('IS451', 'Information and Systems Security', 'Jackson Hall 115', 'Lab'),
       ('MATH212', 'Linear Algebra', 'Nutor Hall 115', 'Lecture'),
       ('MATH212', 'Linear Algebra', 'Apt Hall 217', 'Discussion'),
       ('MATH212', 'Linear Algebra', 'Apt Hall 217', 'Lab'),
       ('MATH101', 'College Algebra', 'Nutor Hall 115', 'Lecture'),
       ('MATH101', 'College Algebra', 'Nutor Hall 216', 'Lecture'),
       ('MATH101', 'College Algebra', 'Nutor Hall 115', 'Discussion'),
       ('MATH121', 'Pre-Calculus I', 'Jackson Lab 222', 'Lecture'),
       ('MATH121', 'Pre-Calculus I', 'Jackson Hall 116', 'Lecture'),
       ('MATH121', 'Pre-Calculus I', 'Science Lab', 'Discussion'),
       ('MATH121', 'Pre-Calculus I', 'Jackson Hall 115', 'Lecture'),
       ('MATH121', 'Pre-Calculus I', 'Jackson Hall 115', 'Discussion'),
       ('MATH121', 'Pre-Calculus I', 'Nutor Hall 100', 'Lecture'),
       ('MATH121', 'Pre-Calculus I', 'Norton-Motulsky 207A', 'Discussion');

INSERT INTO SessionLocationPreferences (CourseCode, CourseName, Location, SessionType)
VALUES 
       ('MATH121', 'Pre-Calculus I', 'Databank Foundation Hall 218', 'Lecture'),
       ('MATH121', 'Pre-Calculus I', 'Fab Lab 203', 'Discussion'),
       ('MATH121', 'Pre-Calculus I', 'Fab Lab 203', 'Lecture'),
       ('MATH122', 'Pre-Calculus II', 'Jackson Hall 116', 'Lecture'),
       ('MATH122', 'Pre-Calculus II', 'Apt Hall 216', 'Lecture'),
       ('MATH122', 'Pre-Calculus II', 'Jackson Hall 115', 'Discussion'),
       ('MATH122', 'Pre-Calculus II', 'Radichel MPR', 'Lecture'),
       ('MATH122', 'Pre-Calculus II', 'Jackson Lab 221', 'Lecture'),
       ('MATH122', 'Pre-Calculus II', 'Nutor Hall 115', 'Discussion'),
       ('MATH122', 'Pre-Calculus II', 'Jackson Hall 115', 'Lecture'),
       ('MATH141', 'Calculus I', 'Jackson Hall 116', 'Lecture'),
       ('MATH141', 'Calculus I', 'Jackson Hall 116', 'Discussion'),
       ('MATH142', 'Calculus II', 'Jackson Hall 116', 'Lecture'),
       ('MATH142', 'Calculus II', 'Jackson Hall 116', 'Discussion'),
       ('MATH144', 'Applied Calculus', 'Jackson Hall 116', 'Lecture'),
       ('MATH144', 'Applied Calculus', 'Jackson Lab 221', 'Lecture'),
       ('MATH144', 'Applied Calculus', 'Bio Lab', 'Discussion'),
       ('MATH144', 'Applied Calculus', 'Jackson Hall 115', 'Lecture'),
       ('MATH145', 'Applied Calculus - Part I', 'Jackson Lab 221', 'Lecture'),
       ('MATH145', 'Applied Calculus - Part I', 'Jackson Hall 116', 'Discussion'),
       ('MATH145', 'Applied Calculus - Part I', 'Nutor Hall 216', 'Lecture'),
       ('MATH145', 'Applied Calculus - Part I', 'Nutor Hall 100', 'Discussion'),
       ('MATH145', 'Applied Calculus - Part I', 'Nutor Hall 100', 'Lecture'),
       ('MATH146', 'Applied Calculus - Part II', 'Jackson Hall 115', 'Lecture'),
       ('MATH146', 'Applied Calculus - Part II', 'Jackson Hall 115', 'Discussion'),
       ('MATH146', 'Applied Calculus - Part II', 'Jackson Hall 116', 'Discussion'),
       ('MATH152', 'Statistics for Engineering and Economics', 'Fab Lab 303', 'Lecture'),
       ('MATH152', 'Statistics for Engineering and Economics', 'Fab Lab 303', 'Discussion'),
       ('MATH161', 'Engineering Calculus', 'Fab Lab 203', 'Lecture'),
       ('MATH161', 'Engineering Calculus', 'Science Lab', 'Lecture'),
       ('MATH211', 'Multivariable Calculus and Linear Algebra', 'Jackson Lab 222', 'Lecture'),
       ('MATH211', 'Multivariable Calculus and Linear Algebra', 'Jackson Lab 222', 'Discussion'),
       ('MATH211', 'Multivariable Calculus and Linear Algebra', 'EE lab', 'Lecture'),
       ('MATH211', 'Multivariable Calculus and Linear Algebra', 'Apt Hall 217', 'Lecture'),
       ('MATH221', 'Statistics', 'Databank Foundation Hall 218', 'Lecture'),
       ('MATH221', 'Statistics', 'Apt Hall 217', 'Discussion'),
       ('MATH221', 'Statistics', 'Apt Hall 217', 'Lecture'),
       ('MATH221', 'Statistics', 'Apt Hall 216', 'Discussion'),
       ('MATH221', 'Statistics', 'Jackson Hall 116', 'Lecture'),
       ('MATH221', 'Statistics', 'Databank Foundation Hall 218', 'Discussion'),
       ('MATH223', 'Quantitative Methods', 'Databank Foundation Hall 218', 'Lecture'),
       ('MATH223', 'Quantitative Methods', 'Nutor Hall 115', 'Discussion'),
       ('MATH251', 'Differential Equations and Numerical Methods', 'Fab Lab 303', 'Discussion'),
       ('MATH251', 'Differential Equations and Numerical Methods', 'Science Lab', 'Lecture');

INSERT INTO SessionLocationPreferences (CourseCode, CourseName, Location, SessionType)
VALUES 
       ('ME101', 'Engineering Mechanics', 'Fab Lab 203', 'Lab'),
       ('ME101', 'Engineering Mechanics', 'Fab Lab 203', 'Lecture'),
       ('ME212', 'Thermodynamics', 'Fab Lab 303', 'Lab'),
       ('ME212', 'Thermodynamics', 'Fab Lab 303', 'Lecture'),
       ('ME212', 'Thermodynamics', 'Databank Foundation Hall 218', 'Lecture'),
       ('ME301', 'Mechanical Machine Design', 'Fab Lab 303', 'Lab'),
       ('ME301', 'Mechanical Machine Design', 'Fab Lab 303', 'Lecture'),
       ('ME311', 'Mechanics of Materials', 'Fab Lab 303', 'Lab'),
       ('ME311', 'Mechanics of Materials', 'Bio Lab', 'Lecture'),
       ('ME311', 'Mechanics of Materials', 'Fab Lab 103', 'Lab'),
       ('ME311', 'Mechanics of Materials', 'Fab Lab 103', 'Lecture'),
       ('ME401', 'Mechanics of Machines & Engineering Vibration', 'Science Lab', 'Lab'),
       ('ME401', 'Mechanics of Machines & Engineering Vibration', 'Fab Lab 303', 'Lecture'),
       ('ME401', 'Mechanics of Machines & Engineering Vibration', 'Fab Lab 103', 'Discussion'),
       ('ME401', 'Mechanics of Machines & Engineering Vibration', 'Fab Lab 103', 'Lecture'),
       ('ME412', 'Advanced Thermodynamics', 'D-Lab 102', 'Lab'),
       ('ME412', 'Advanced Thermodynamics', 'Bio Lab', 'Lecture'),
       ('ME412', 'Advanced Thermodynamics', 'Norton-Motulsky 207B', 'Lecture'),
       ('ME422', 'Heat Transfer', 'Science Lab', 'Lab'),
       ('ME422', 'Heat Transfer', 'Science Lab', 'Lecture'),
       ('ME422', 'Heat Transfer', 'Bio Lab', 'Lab'),
       ('ME422', 'Heat Transfer', 'Bio Lab', 'Lecture'),
       ('ME431', 'Fluid Mechanics', 'Bio Lab', 'Lecture'),
       ('ME431', 'Fluid Mechanics', 'D-Lab 102', 'Lab'),
       ('ME432', 'Computational Fluid Dynamics', 'Science Lab', 'Lab'),
       ('ME432', 'Computational Fluid Dynamics', 'Science Lab', 'Lecture'),
       ('ME432', 'Computational Fluid Dynamics', 'Norton-Motulsky 207B', 'Lecture'),
       ('ME434', 'Hydraulic & Fluid Machinery', 'D-Lab 102', 'Lab'),
       ('ME434', 'Hydraulic & Fluid Machinery', 'EE lab', 'Lecture'),
       ('ME434', 'Hydraulic & Fluid Machinery', 'Fab Lab 103', 'Lab'),
       ('ME434', 'Hydraulic & Fluid Machinery', 'Fab Lab 103', 'Lecture'),
       ('ME441', 'Manufacturing Processes', 'Fab Lab 203', 'Lecture'),
       ('ME441', 'Manufacturing Processes', 'Bio Lab', 'Lab'),
       ('ME442', 'Computer Aided Design and Manufacturing', 'Fab Lab 303', 'Lab'),
       ('ME442', 'Computer Aided Design and Manufacturing', 'Fab Lab 303', 'Lecture'),
       ('ME444', 'Advanced Mechanical Machine Design', 'Bio Lab', 'Lecture'),
       ('ME444', 'Advanced Mechanical Machine Design', 'Bio Lab', 'Lab'),
       ('ME444', 'Advanced Mechanical Machine Design', 'D-Lab 102', 'Lab'),
       ('ME444', 'Advanced Mechanical Machine Design', 'Science Lab', 'Lecture'),
       ('ME445', 'Machine Shop and Factory Design', 'Radichel MPR', 'Lab'),
       ('ME445', 'Machine Shop and Factory Design', 'Bio Lab', 'Lecture'),
       ('ME445', 'Machine Shop and Factory Design', 'Norton-Motulsky 207B', 'Lecture'),
       ('POLS322', 'China-Africa Relations', 'Jackson Lab 221', 'Lecture'),
       ('POLS322', 'China-Africa Relations', 'Norton-Motulsky 207A', 'Discussion'),
       ('POLS334', 'Introduction to Public Policy', 'Jackson Hall 115', 'Lecture'),
       ('POLS334', 'Introduction to Public Policy', 'Jackson Hall 115', 'Discussion'),
       ('POLS221', 'African Philosophical Thought', 'Nutor Hall 100', 'Lecture'),
       ('POLS221', 'African Philosophical Thought', 'Nutor Hall 115', 'Discussion'),
       ('POLS234', 'Comparative Politics', 'Jackson Lab 222', 'Lecture'),
       ('POLS234', 'Comparative Politics', 'Apt Hall 216', 'Discussion'),
       ('POLS237', 'African Trade and Regional Integration', 'Apt Hall 216', 'Lecture'),
       ('POLS237', 'African Trade and Regional Integration', 'Apt Hall 217', 'Discussion'),
       ('POLS332', 'Governance in Africa', 'Nutor Hall 100', 'Lecture'),
       ('POLS332', 'Governance in Africa', 'Fab Lab 303', 'Discussion'),
       ('SC113', 'Physics: Electromagnetism', 'Science Lab', 'Lab'),
       ('SC113', 'Physics: Electromagnetism', 'Science Lab', 'Lecture'),
       ('SC221', 'Materials Science & Chemistry', 'Science Lab', 'Lecture'),
       ('SC221', 'Materials Science & Chemistry', 'Science Lab', 'Lab');

INSERT INTO SessionLocationPreferences (CourseCode, CourseName, Location, SessionType)
VALUES 
       ('SOAN322', 'African Cultural Institutions', 'Jackson Hall 116', 'Lecture'),
       ('SOAN322', 'African Cultural Institutions', 'Jackson Lab 222', 'Discussion'),
       ('SOAN322', 'African Cultural Institutions', 'Apt Hall 217', 'Lecture'),
       ('SOAN322', 'African Cultural Institutions', 'Jackson Hall 115', 'Discussion'),
       ('SOAN111', 'Leadership Seminar I: What Makes a Good Leader?', 'Nutor Hall 115', 'Discussion'),
       ('SOAN111', 'Leadership Seminar I: What Makes a Good Leader?', 'Norton-Motulsky 207A', 'Lecture'),
       ('SOAN111', 'Leadership Seminar I: What Makes a Good Leader?', 'Norton-Motulsky 207A', 'Discussion'),
       ('SOAN111', 'Leadership Seminar I: What Makes a Good Leader?', 'Fab Lab 303', 'Discussion'),
       ('SOAN111', 'Leadership Seminar I: What Makes a Good Leader?', 'Jackson Lab 222', 'Lecture'),
       ('SOAN111', 'Leadership Seminar I: What Makes a Good Leader?', 'Jackson Lab 221', 'Discussion'),
       ('SOAN111', 'Leadership Seminar I: What Makes a Good Leader?', 'Nutor Hall 100', 'Discussion'),
       ('SOAN111', 'Leadership Seminar I: What Makes a Good Leader?', 'Jackson Lab 221', 'Lecture'),
       ('SOAN111', 'Leadership Seminar I: What Makes a Good Leader?', 'Norton-Motulsky 207A', 'Seminar'),
       ('SOAN111', 'Leadership Seminar I: What Makes a Good Leader?', 'Jackson Lab 222', 'Seminar'),
       ('SOAN111', 'Leadership Seminar I: What Makes a Good Leader?', 'D-Lab 102', 'Seminar'),
       ('SOAN111', 'Leadership Seminar I: What Makes a Good Leader?', 'Nutor Hall 115', 'Seminar'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Nutor Hall 115', 'Seminar'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Apt Hall 216', 'Discussion'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Nutor Hall 100', 'Seminar'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Jackson Hall 115', 'Discussion'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'D-Lab 102', 'Discussion'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Jackson Lab 222', 'Discussion'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Apt Hall 216', 'Seminar'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Nutor Hall 100', 'Discussion'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Apt Hall 217', 'Seminar'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Radichel MPR', 'Discussion'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Jackson Lab 222', 'Seminar'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Nutor Hall 216', 'Seminar'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Nutor Hall 216', 'Discussion'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Norton-Motulsky 207A', 'Seminar'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Apt Hall 217', 'Discussion'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Science Lab', 'Seminar'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Fab Lab 203', 'Seminar'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Databank Foundation Hall 218', 'Discussion'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Nutor Hall 115', 'Discussion'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Jackson Hall 115', 'Seminar'),
       ('SOAN211', 'Leadership Seminar II: Rights, Ethics and Rule of Law', 'Jackson Lab 221', 'Seminar'),
       ('SOAN411', 'Leadership Seminar IV: Leadership as Service', 'Norton-Motulsky 207A', 'Seminar'),
       ('SOAN411', 'Leadership Seminar IV: Leadership as Service', 'Jackson Lab 222', 'Seminar'),
       ('SOAN411', 'Leadership Seminar IV: Leadership as Service', 'Nutor Hall 115', 'Seminar'),
       ('SOAN411', 'Leadership Seminar IV: Leadership as Service', 'Norton-Motulsky 207B', 'Seminar'),
       ('SOAN411', 'Leadership Seminar IV: Leadership as Service', 'Jackson Hall 116', 'Seminar'),
       ('SOAN411', 'Leadership Seminar IV: Leadership as Service', 'Fab Lab 203', 'Seminar'),
       ('SOAN411', 'Leadership Seminar IV: Leadership as Service', 'Nutor Hall 100', 'Seminar'),
       ('SOAN411', 'Leadership Seminar IV: Leadership as Service', 'Jackson Hall 115', 'Seminar'),
       ('SOAN411', 'Leadership Seminar IV: Leadership as Service', 'Apt Hall 217', 'Seminar');
    

