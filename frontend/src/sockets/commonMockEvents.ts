/* eslint-disable vue/max-len */
/* eslint-disable max-len */
export const commonMockEvents = [
	{id: 'failure', data: '{"messageType":"failure","message":"Error encountered"}'},
	{id: 'test-passthrough', data: '{"messageType":"test-passthrough","message":"received test-passthrough event"}'},
	{
		id: "available-patients",
		data: JSON.stringify({
			"messageType": "available-patients",
			"availablePatients": [{
				"code": 1001,
				"personalDetails": "Annkatrin Rohde 01.05.1989 Aulgasse 75, 53721 Siegburg",
				"injury": "Sch\u00fcrfwunden beide Arme und Kopf; nicht mehr wesentlich blutend; leichte Bewegungseinschr\u00e4nkung im li. Ellbogengelenk",
				"biometrics": "weiblich; ca. 27; braune Augen, braune Haare, 1,60 m",
				"triage": "-",
				"mobility": "initial gehf\u00e4hig",
				"preexistingIllnesses": "v. Jahren unklare An\u00e4mie; v. 2 J. OSG- Fraktur re.",
				"permanentMedication": "keine Medikamente",
				"currentCaseHistory": "kommt selbst zu Fu\u00df ins KrHs: bisher keine medizinische Versorgung, Taschentuch auf Wunde.",
				"pretreatment": "keine keine"
			}, {
				"code": 1002,
				"personalDetails": "Sami Hauder 02.10.1954 Geldernstra\u00dfe 121, 50739 K\u00f6ln",
				"injury": "",
				"biometrics": "m\u00e4nnlich; ca. 62; braune Augen, 1,74 cm, schwarze Haare, Brille",
				"triage": "-",
				"mobility": "initial gehf\u00e4hig",
				"preexistingIllnesses": "Hypertonie; KHK; v. 4 J. MI und ACVB;",
				"permanentMedication": "Nitro; ACE-Hemmer; ASS; Diuretikum",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: seit 3 Std. AP; 3 Hub Nitro bekommen, deutliche Schmerzreduktion; heute viel Stress gehabt; EKG war unauff\u00e4llig. 500ml Infusion pr\u00e4klinisch bekommen",
				"pretreatment": "1xZugang, Nitrat, Rettungsdienst-Sauerstoff,"
			}, {
				"code": 1003,
				"personalDetails": "Karoline Klausm\u00fcller 05.05.1934 Am F\u00f6rderturm 33a, 46049 Oberhausen",
				"injury": "Prellmarke Schulter re.; keine offene Wunde; Beweglichkeit schmerzhaft eingeschr\u00e4nkt",
				"biometrics": "weiblich; ca. 82; wei\u00dfhaarig, blaue Augen, Brille, 171 cm",
				"triage": "-",
				"mobility": "initial gehf\u00e4hig",
				"preexistingIllnesses": "Gallensteine; Diab. mell.",
				"permanentMedication": "Diuretikum, Baldrian, Benzodiazepin z.N., Insulin;",
				"currentCaseHistory": "Pat. hat sich selbst gerettet und ist selbstst\u00e4ndig zu Fu\u00df ins KrHs gekommen; Schulterschmerzen rechts; DMS oB",
				"pretreatment": "keine keine"
			}, {
				"code": 1004,
				"personalDetails": "Helena Raedder 15.03.1964 Albert-Einstein-Str. 34, 06122 Halle",
				"injury": "ca. 8 cm gro\u00dfe, weit klaffende Kopfplatzwunde re. temporal, blutet noch; im Wundgrund vermutlich Knochensplitter sichtbar.",
				"biometrics": "weiblich; ca. 52; blond, braune Augen, Brille, 1,82 m",
				"triage": "3",
				"mobility": "initial gehf\u00e4hig",
				"preexistingIllnesses": "funktionelle Herzbeschwerden; beginnender Bechterew",
				"permanentMedication": "Schlafmittel",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: habe eine Deckenplatte vor den Kopf bekommen; Verband durchgeblutet; nicht bewusstlos gewesen.",
				"pretreatment": "Wundversorgung,"
			}, {
				"code": 1005,
				"personalDetails": "keine zu finden",
				"injury": "subtotale Amputationsverletzung li. Arm kurz oberhalb des Ellbogengelenks, massiv arteriell blutend; Prellmarken Thorax li.; V.a. Rippenfraktur links; Unterschenkelprellmarken li.",
				"biometrics": "m\u00e4nnlich; ca. 45; blaue Augen, schwarzhaarig, 1,84 m",
				"triage": "-",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "nicht zu erheben",
				"permanentMedication": "nicht zu erheben",
				"currentCaseHistory": "Pat. wird von Taxi gebracht; bisher nicht versorgt, nur Handtuch um die Wunde gewickelt; im Auto mind. 2 l Blut.",
				"pretreatment": "keine keine"
			}, {
				"code": 1006,
				"personalDetails": "Georg Henke 26.03.1960 Otto-Fischer-Str. 2, 50674 K\u00f6ln",
				"injury": "gro\u00dfe Kopfplatzwunde frontal, noch wenig blutend; Monokelh\u00e4matom rechtes Auge",
				"biometrics": "m\u00e4nnlich; ca. 56; schwarzhaarig, 1,79 m, blaue Augen",
				"triage": "-",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "nicht zu erheben",
				"permanentMedication": "nicht zu erheben",
				"currentCaseHistory": "wird von PrivatPKW gebracht; habe einen Holzbalken auf den Kopf bekommen und sei sofort zusammengebrochen.",
				"pretreatment": "keine keine"
			}, {
				"code": 1007,
				"personalDetails": "Birgit Bauer 06.08.1958 Am Weidenbach 25, 53229 Bonn",
				"injury": "geschlossene Oberschenkelfraktur bds.; gro\u00dfe Weichteilquetschung Unterschenkel re.; instabiler Thorax re. lateral; Prellmarken Becken, Becken aber stabil; SHT mit Kopfplatzwunde occipital",
				"biometrics": "weiblich; ca. 58; blaue Augen, grauhaarig, 163 cm",
				"triage": "1",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "nicht bekannt",
				"permanentMedication": "nicht bekannt",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: von Tr\u00fcmmerteilen getroffen, initial bewusstlos, prim\u00e4r intubiert, 1000 VEL erhalten, Narkose mit Fenta, Dormicum; kreislaufstabil",
				"pretreatment": "1xZugang, 2xVEL, Analgetikum, Sedativum, k\u00fcnstlicher Atemweg, Rettungsdienst-Beatmung, Rettungsdienst- Stifneck, Rettungsdienst-Vacuum-Matratze,"
			}, {
				"code": 1008,
				"personalDetails": "Petra Stelzyk 18.10.1959 Feldm\u00fchlestra\u00dfe 24, 53859 Niederkassel",
				"injury": "gro\u00dfe Prellmarke rechte Flanke; Abdomen gespannt; H\u00e4matom Unterbauch",
				"biometrics": "weiblich; ca. 57; schwarzhaarig, 1,79 m, blaue Augen",
				"triage": "1",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "Hypertonie; Diab. Mell.",
				"permanentMedication": "Insulin, B-Blocker;",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: massives Abdominaltrauma; inital st\u00e4rkste Schmerzen; Dyspnoe; 500ml Infusion pr\u00e4klinisch; nach Analgesie Besserung des Schmerzes",
				"pretreatment": "1xZugang, 1xVEL, Analgetikum, Rettungsdienst- Sauerstoff,"
			}, {
				"code": 1009,
				"personalDetails": "Ludger G\u00f6hlke 11.05.1938 K\u00f6nigswall 15, 44137 Dortmund",
				"injury": "rechte Clavikula lateral 3-gradig offen frakturiert; gro\u00dfe Sch\u00fcrfwunde proximaler Oberarm re.; instabiler Thorax re.; gro\u00dfe Sch\u00fcrfwunde rechter Thorax, nur noch wenig blutend",
				"biometrics": "m\u00e4nnlich; ca. 78; schwarzgraue Haare, gr\u00fcne Augen, 1,69 m",
				"triage": "1",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "verm. Infarkt v. 4 J.",
				"permanentMedication": "nicht erhebbar",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: wegen st\u00e4rkster Schmerzen und Luftnot intubiert; Schulter in Narkose spontan reponiert, Narkose mit Fentanyl, Ketanest, Dormicum; 500ml Infusion pr\u00e4klinisch bekommen",
				"pretreatment": "1xZugang, 1xVEL, Wundversorgung, Analgetikum, Sedativum, k\u00fcnstlicher Atemweg, Rettungsdienst- Beatmung,"
			}, {
				"code": 1010,
				"personalDetails": "Marlene Wei\u00df 28.08.1934 Am Weidenbach 27, 53229 Bonn",
				"injury": "",
				"biometrics": "weiblich; ca. 82; graublond, 1,75 m, blaue Augen, Brille",
				"triage": "-",
				"mobility": "initial bettl\u00e4gerig",
				"preexistingIllnesses": "Nikotinabusus; Diab. mell.; Hypertonie",
				"permanentMedication": "Digitalis, Salbutamol",
				"currentCaseHistory": "Magernresektion bei CA v.12d, postOP: MOV, ANV, Dialyse, offener Bauch; beginnende DIC, Vorgestern akute Blutung a.mesenterica, operativ versorgt; leichte Besserung seit gestern, Kreislauf mit Arterenol stabil, Ausscheidung kommt langsam; Beatmung stabil",
				"pretreatment": "2xZugang, ZVK, 1xVEL, AnalgetikumP, SedativumP, KatecholaminP, AntikoagulanzP, k\u00fcnstlicher Atemweg, Beatmung,"
			}, {
				"code": 1011,
				"personalDetails": "Alessandro Giacomo 18.08.1932 Friedrich- Lueg- Stra\u00dfe 8, 44867 Bochum",
				"injury": "",
				"biometrics": "m\u00e4nnlich; ca. 84; grauhaarig, Brille, 1,72 m, braune Augen",
				"triage": "-",
				"mobility": "initial bettl\u00e4gerig",
				"preexistingIllnesses": "HRST, Herzinsuffizienz",
				"permanentMedication": "Nitro, Amiodaron, Kalium",
				"currentCaseHistory": "KnieTEP vor 7 Tagen, postoperative Thrombose, gestern fulminante Lungenembolie; seit dem beatmet",
				"pretreatment": "2xZugang, ZVK, 2xVEL, AnalgetikumP, KatecholaminP, NarkotikumP, AntikoagulanzP, k\u00fcnstlicher Atemweg, Beatmung,"
			}, {
				"code": 1012,
				"personalDetails": "Lena Krings 20.09.1954 Altenessener Str. 606, 45329 Essen",
				"injury": "Druckschmerz \u00fcber der HWS c2-4; leichte Kribbelpar\u00e4sthesien in beiden H\u00e4nden, Kraft oB.; Haut intakt",
				"biometrics": "weiblich; ca. 62; blaue Augen, blond, 1,68, extrem adip\u00f6s",
				"triage": "3",
				"mobility": "initial gehf\u00e4hig",
				"preexistingIllnesses": "Hashimoto-Thyreoiditis",
				"permanentMedication": "keine Medikamente",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: habe einen Balken auf den Nacken bekommen; keine Bewusstlosigkeit.",
				"pretreatment": "Rettungsdienst-Stifneck,"
			}, {
				"code": 1013,
				"personalDetails": "Herrmann Miller 26.10.1942 Trankgasse 11, 50667 K\u00f6ln",
				"injury": "Sch\u00fcrfwunden an beiden Beinen, kann nicht auftreten; Platzwunde Ellenbogen li.",
				"biometrics": "m\u00e4nnlich; ca. 74; schwarzgraue Haare, braune Augen, 179 cm",
				"triage": "3",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "COPD; Hyperlipid\u00e4mie; postthrombotisches Syndrom re.",
				"permanentMedication": "Theophylin, Kortison, Salbutamol, ASS",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: war in der Trib\u00fcne mit den Beinen eingeklemmt, musste mit Stemmeisen befreit werden; starke Schmerzen beim Auftreten; keine Bewusstlosigkeit.",
				"pretreatment": "keine keine"
			}, {
				"code": 1014,
				"personalDetails": "Christopher Krings 16.07.1961 Altenessener Str. 606, 45329 Essen",
				"injury": "gro\u00dfe Holzsplitter in beiden H\u00e4nden; gro\u00dfe Quetschwunde mit Holzsp\u00e4nen rechter Unterschenkel",
				"biometrics": "m\u00e4nnlich; ca. 55; blond, blaugraue Augen, Brille, 1,80 m",
				"triage": "3",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "keine",
				"permanentMedication": "keine Medikament",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: hat bei der Rettung von Patienten geholfen und sich dabei verletzt.",
				"pretreatment": "Wundversorgung,"
			}, {
				"code": 1015,
				"personalDetails": "Heide Kr\u00f6mer 07.06.1993 Freiherr-von-Stein-Str. 211, 45133 Essen",
				"injury": "Fehlstellung Unterarm links; ca 1 cm lange Prellmarke an der Stirn",
				"biometrics": "weiblich; ca. 23; blaue Augen, blond, 174 cm",
				"triage": "3",
				"mobility": "initial gehf\u00e4hig",
				"preexistingIllnesses": "App. vor 4 J; allergisches Asthma",
				"permanentMedication": "keine Dauermedikaiton",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: V.a. Fraktur li Unterarm, keine Fehlstellung, DMS peripher oB.;",
				"pretreatment": "Wundversorgung, Rettungsdienst-Extremit\u00e4tenschiene,"
			}, {
				"code": 1016,
				"personalDetails": "Nezrin Azzouni 17.07.1941 Rudolf-Diesel-Stra\u00dfe 32, 51149 K\u00f6ln",
				"injury": "ca 5 cm lange verschmutzte Kopfplatzwunde temporal re.",
				"biometrics": "m\u00e4nnlich; ca. 75; graublond, blaue Augen, 180 cm",
				"triage": "3",
				"mobility": "initial gehf\u00e4hig",
				"preexistingIllnesses": "Apoplex vor 12 J. ohne Residuen; Colon-CA vor 4 J.; Diab. Mell.",
				"permanentMedication": "\u00df-Blocker, Statin; Metformin; ASS",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: hat wohl Gegenstand gegen den Kopf bekommen; keine Bewusstlosigkeit, lief aber zunn\u00e4chst verwirrt umher",
				"pretreatment": "Wundversorgung,"
			}, {
				"code": 1017,
				"personalDetails": "Freddy Schulze 16.02.1957 Am Dinaswerk 4a, 53179 Bad Godesberg",
				"injury": "starke Schwellung im re. Sprunggelenk; Fehlstellung im Handgelenk li.; Sch\u00fcrfwunden linker Arm; DMS Hand und Fu\u00df oB.",
				"biometrics": "m\u00e4nnlich; ca. 59; schwarzhaarig, Brille, braune Augen, ca. 170 cm",
				"triage": "2",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "Depressionen; Hypertonie",
				"permanentMedication": "Nikotinpflaster; Antidepressivum; Diuretikum",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: War unter Trib\u00fcne eingeklemmt, 500ml Infusion 1xAnalgesie und Extremit\u00e4tenschiene pr\u00e4klinisch erhalten",
				"pretreatment": "1xZugang, 1xVEL, Analgetikum, Rettungsdienst- Extremit\u00e4tenschiene,"
			}, {
				"code": 1018,
				"personalDetails": "Eric Weilandt 06.07.1967 Moltkestr. 43, 53173 Bonn",
				"injury": "Monokelh\u00e4matom rechts; Prellung Nasenbein; occipitale Kopfplatzwunde; offene Sprunggelenks# li.;",
				"biometrics": "m\u00e4nnlich; ca. 49; Glatze, braune Augen, 1,76 m",
				"triage": "2",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "Prostatahypertrophie; vor 10 d beginnende Pneumonie, antibiotisch behandelt",
				"permanentMedication": "Prostatamed; Antibiotikum;",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: Pat. von Deckenteilen getroffen, initial kurz bewusstlos, nach 3-4 min wieder aufgeklart, keine Infusion nur Zugang",
				"pretreatment": "1xZugang, Wundversorgung, Analgetikum, Rettungsdienst-Extremit\u00e4tenschiene,"
			}, {
				"code": 1019,
				"personalDetails": "Gundula Stra\u00dfen 24.02.1953 Eschweiler Stra\u00dfe 2, 50354 H\u00fcrth",
				"injury": "Schulterprellung re.; geschlossene OA# re mit massivem H\u00e4matom; Unterschenkelquetschung re.; Prellmarke Becken re.",
				"biometrics": "weiblich; ca. 63; braune Augen, braunhaarig, 1,82 m",
				"triage": "2",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "Epilepsie, medikament\u00f6s gut eingestellt; Psoriasis; M. Crohn",
				"permanentMedication": "Hormonpr\u00e4parat; Antiepileptikum",
				"currentCaseHistory": "wird vom Krankentransport gebracht: Pat. von Eisentr\u00e4ger an der rechten Seite getroffen worden; initial hysterisch gewesen.",
				"pretreatment": "keine keine"
			}, {
				"code": 1020,
				"personalDetails": "Danuta Krings 30.11.1955 Altenessener Str. 606, 45329 Essen",
				"injury": "Oberschenkelschaft# re.; Sch\u00fcrfwunden beide Arme; Prellmarken H\u00fcfte re.",
				"biometrics": "weiblich; ca. 60; braune Haare, braune Augen, 1,77 m",
				"triage": "2",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "Hepatitis C; Hyperlipid\u00e4mie",
				"permanentMedication": "Interferon; Statin; Diuretikum; Kortison",
				"currentCaseHistory": "wird vom Rettungsdienst gebracht: Pat. von Holzbalken getroffen worden, keine Bewusstlosigkeit",
				"pretreatment": "Rettungsdienst-Extremit\u00e4tenschiene,"
			}, {
				"code": 1021,
				"personalDetails": "Manuela Merthens 20.11.1955 Langemarckstr. 9, 45141 Essen",
				"injury": "massiv blutende Kopfplatzwunde temporal re.; schwere Weichteilverletzung Unterarm re stark hellrot blutend; Durchblutung re Hand gest\u00f6rt",
				"biometrics": "weiblich; ca. 60; blaue Augen, graue Haare, 1,63 m",
				"triage": "-",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "Schilddr\u00fcsen-CA vor 6 J.; KHK",
				"permanentMedication": "Thyroxin; Loperamid; ASS;",
				"currentCaseHistory": "wird von Angeh\u00f6rigen in einem Einkaufswagen gebracht: Sei von herabst\u00fcrzenden Deckenteilen verletzt worden",
				"pretreatment": "keine keine"
			}, {
				"code": 1022,
				"personalDetails": "Harald Bonk 23.05.1930 Friedrichstr. 145, 40217 D\u00fcsseldorf",
				"injury": "perianale Schwellung und R\u00f6tung",
				"biometrics": "m\u00e4nnlich; ca. 86; wei\u00dfe Haare, braune Augen, 159 cm, Brille",
				"triage": "-",
				"mobility": "initial bedingt gehf\u00e4hig",
				"preexistingIllnesses": "Demenz; Diab. mell.; 3x periproktitischer Abszess",
				"permanentMedication": "Schilddr\u00fcsenmed; \u00df- Blocker, Diuretikum; Benzodiazepin",
				"currentCaseHistory": "seit 4 Tagen Schmerzen perianal; heute abend mit Abszess vorgestellt, soll noch diese Nacht gespalten werden.",
				"pretreatment": "1xZugang, 1xVEL,"
			}, {
				"code": 1023,
				"personalDetails": "Sven Dittmer 04.01.1965 Ahrensplatz 1, 40474 D\u00fcsseldorf",
				"injury": "",
				"biometrics": "m\u00e4nnlich; ca. 51; graue Haare, Brille, gr\u00fcne Augen, ca. 1,60 m",
				"triage": "-",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "DM; AVK; KHK; Exsikkose",
				"permanentMedication": "orale Antidiabetika; Marcumar; Nitro; ACE- Hemmer",
				"currentCaseHistory": "wurde vom Rettundgsdienst unterzuckert aufgefunden BZ<20; war nach Glucose iv noch verwirrt",
				"pretreatment": "1xZugang, 1xVEL, Glucose,"
			}, {
				"code": 1024,
				"personalDetails": "Christa M\u00f6ller-Lutterbeck 07.04.1942 Am Hellenkreuz 3, 53332 Bornheim",
				"injury": "",
				"biometrics": "weiblich; ca. 74; gr\u00fcne Augen, blond, 1,68 m, adip\u00f6s",
				"triage": "-",
				"mobility": "initial bedingt gehf\u00e4hig",
				"preexistingIllnesses": "schwer einstellbare Hypertonie; KHK",
				"permanentMedication": "\u00df-Blocker; Diuretikum; ACE-Hemmer; ASS",
				"currentCaseHistory": "gestern Abend zu Hause hypertensiv entgleist. RR 275/135 mit Sehst\u00f6rungen und Kopfschmerzen, nach Urapidil pr\u00e4klinisch langsam Besserung",
				"pretreatment": "1xZugang, 1xVEL,"
			}, {
				"code": 1025,
				"personalDetails": "Amelie Sch\u00f6n 21.09.1938 S\u00fcdring 79, 46242 Bottrop",
				"injury": "",
				"biometrics": "weiblich; ca. 78; schwarzgraue Haare, blaugraue Augen, 1,69 m",
				"triage": "-",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "schwere Demenz mit Weglauftendenz; Herzinsuffizienz; Exsikkose",
				"permanentMedication": "Antidepressiva; Verapamil; ASS;",
				"currentCaseHistory": "gestern aus dem Heim wegen Exsikkose und zunehmender Eintr\u00fcbung gekommen.",
				"pretreatment": "1xZugang, 1xVEL,"
			}, {
				"code": 1026,
				"personalDetails": "Frank Binder 06.04.1965 Heidestr. 15, 45476 M\u00fclheim",
				"injury": "verschieden alte Wunden",
				"biometrics": "m\u00e4nnlich; ca. 51; graue Haare, Brille, braune Augen, 1,60 m",
				"triage": "-",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "bekannter Alkoholiker",
				"permanentMedication": "nicht bekannt",
				"currentCaseHistory": "gestern Abend mit 3,5 Promill somnolent aufgenommen",
				"pretreatment": "1xZugang, 1xVEL, Sauerstoff,"
			}, {
				"code": 1027,
				"personalDetails": "Jakob Roth 19.11.1942 M\u00fclheimer Stra\u00dfe 20, 46049 Oberhausen",
				"injury": "",
				"biometrics": "m\u00e4nnlich; ca. 74; braun\u00e4ugig, 164 cm, grauhaarig, Brille",
				"triage": "-",
				"mobility": "initial gehf\u00e4hig",
				"preexistingIllnesses": "KHK; v 3 Mo. Infarkt; Diab. mell.",
				"permanentMedication": "Insulin, \u00df-Blocker; ASS, Clopidogrel",
				"currentCaseHistory": "vor 2 Stunden mit Angina pectoris aufgenommen, bisher TropT neg, Aufnahme- EKG neg.",
				"pretreatment": "1xZugang, 1xVEL, Nitrat, Antikoagulanz,"
			}, {
				"code": 1028,
				"personalDetails": "Tom P\u00fctz 04.10.1986 Lockhofstra\u00dfe 13, 45881 Gelsenkirchen",
				"injury": "",
				"biometrics": "m\u00e4nnlich; ca. 30; 1,72 m, braune Augen, blonde Haare",
				"triage": "-",
				"mobility": "initial bedingt gehf\u00e4hig",
				"preexistingIllnesses": "M. Crohn seit 5 J.",
				"permanentMedication": "Kortison",
				"currentCaseHistory": "gestern Mittag mit Sub-Ileus gekommen. Bisher nicht abgef\u00fchrt",
				"pretreatment": "1xZugang, 1xVEL,"
			}, {
				"code": 1029,
				"personalDetails": "Ulrike Rothe 23.04.1940 Ruhrtalstr. 85, 45239 Essen",
				"injury": "",
				"biometrics": "weiblich; ca. 76; grauhaarig, blaue Augen, 1,79 m",
				"triage": "-",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "COPD; Heimsauerstofftherapie",
				"permanentMedication": "Kortison, Salbutamol, Berotec",
				"currentCaseHistory": "gestern Abend mit dekompensierter COPD vom Rettungsdienst gebracht, seit Tagen Erk\u00e4ltung, jetzt Pneumonie",
				"pretreatment": "1xZugang, 1xVEL, Antibiotikum, Sauerstoff,"
			}, {
				"code": 1030,
				"personalDetails": "Benno Stern 13.12.1987 In den Diken 7-9, 40472 D\u00fcsseldorf",
				"injury": "",
				"biometrics": "m\u00e4nnlich; ca. 28; blond, 1,70 m, blaue Augen, Brille",
				"triage": "-",
				"mobility": "initial gehf\u00e4hig",
				"preexistingIllnesses": ";bek. Psychose, mehrfach Suizidversuche",
				"permanentMedication": "Antipsychotika, sonstige Psychopharmaka",
				"currentCaseHistory": "kommt selbstst\u00e4ndig ins KrHs: Habe Verfolgungswahn und aktuell Suizidgedanken",
				"pretreatment": "keine keine"
			}, {
				"code": 1031,
				"personalDetails": "Viola Rehmann 06.01.1977 S\u00fcrther Str. 92, 50996 K\u00f6ln",
				"injury": "erhebliche Beinumfangsdifferenz bis hoch zum Oberschenkel und deutliche R\u00f6tung der gesamten Wade; Druckschmerz am gesamten Bein",
				"biometrics": "weiblich; ca. 39; 1,64 m, blond, braune Augen",
				"triage": "-",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "Achalasie; Gallensteine; vor 6 Wo Arthroskopie Knie",
				"permanentMedication": "Hormonpr\u00e4parat; Protonenpumpenblocker, Nikotinabusus (60/d).",
				"currentCaseHistory": "kommt selbstst\u00e4ndig ins KrHs: seit gestern fr\u00fch zunehmende Schmerzen im rechten Unterschenkel.",
				"pretreatment": "keine keine"
			}, {
				"code": 1032,
				"personalDetails": "Erich Weilandt 24.03.1949 Schederhofstr. 59, 45145 Essen",
				"injury": "",
				"biometrics": "m\u00e4nnlich; ca. 67; Glatze, blaue Augen, 1,85 m",
				"triage": "-",
				"mobility": "initial gehf\u00e4hig",
				"preexistingIllnesses": "KHK; vor 2 J. MI mit VF und CPR; seit dem ICD, bisher nie ausgel\u00f6st",
				"permanentMedication": "ASS; Amiodaron; Clopidogrel; Nitro;",
				"currentCaseHistory": "kommt selbstst\u00e4ndig in Krhs: 3-malige Ausl\u00f6sung des ICD vor 30 min., bei zweiter Ausl\u00f6sung kurze Bewusstlosigkeit; da kein Rettungsdienst kam, ging er zu Fu\u00df ins KrHs",
				"pretreatment": "keine keine"
			}, {
				"code": 1033,
				"personalDetails": "Ewald Orlowski 06.04.1956 Flottenstr. 15, 40229 D\u00fcsseldorf",
				"injury": "",
				"biometrics": "m\u00e4nnlich; ca. 60; 1,64 m, blaue Augen, blond",
				"triage": "-",
				"mobility": "initial bettl\u00e4gerig",
				"preexistingIllnesses": "COPD; Nikotinabusus; Z.n. BronchialCA vor 1 J; Pneumonektomie li. Oberlappen",
				"permanentMedication": "Theophylin, Kortison, Salbutamol,",
				"currentCaseHistory": "wegen Dekompensation im Rahmen eines Infektes seit 17 Tagen beatmet, 3 erfolglose Weaningversuche, wartet jetzt auf einen Weaningplatz.",
				"pretreatment": "1xZugang, ZVK, 2xVEL, Kortikosteroid, Antikoagulanz, AnalgetikumP, SedativumP, AntiasthmatikumP, k\u00fcnstlicher Atemweg, Beatmung,"
			}, {
				"code": 1034,
				"personalDetails": "Andrea Puzko 05.04.1970 Moltkestr. 43, 53173 Bonn",
				"injury": "",
				"biometrics": "weiblich; ca. 46; braune Haare, braune Augen, 1,53 m, extrem adip\u00f6s",
				"triage": "-",
				"mobility": "initial bettl\u00e4gerig",
				"preexistingIllnesses": "vor 6 J. MammaCA mit OP und Chemo; vor 3 Mo. Myocarditis",
				"permanentMedication": "Hormonpr\u00e4parat; ASS",
				"currentCaseHistory": "v. 29 Tagen CPR bei prim\u00e4rem VF; Apallisches Syndrom, CPAP-Beatmet; wartet auf Heimbeatmungsplatz",
				"pretreatment": "1xZugang, 1xVEL, Antikoagulanz, k\u00fcnstlicher Atemweg, Beatmung,"
			}, {
				"code": 1035,
				"personalDetails": "Michael Conrads 15.06.1966 Am Weinhaus 15, 40882 Ratingen",
				"injury": "gro\u00dfe infizierte Wunde am linken Unterschenkel",
				"biometrics": "m\u00e4nnlich; ca. 50; blaue Augen, blond, 174 cm, Brille",
				"triage": "-",
				"mobility": "initial bettl\u00e4gerig",
				"preexistingIllnesses": "Alkoholabh\u00e4ngigkeit; Leberzirrhose; vor 5 J. Magenresektion bei CA",
				"permanentMedication": "Insulin,",
				"currentCaseHistory": "aktuell hepatische Enzephalopathie bei Leberzirrhose, beginnendes Kompartmensyndrom linker Unterschenkel, DMS noch oB.",
				"pretreatment": "1xZugang, ZVK, 2xVEL, Antibiotikum, SedativumP, AntikoagulanzP, InsulinP, Sauerstoff,"
			}, {
				"code": 1036,
				"personalDetails": "Therese Zimmermann 09.02.1946 M\u00fcnstermannstra\u00dfe 2, 45357 Essen",
				"injury": "",
				"biometrics": "weiblich; ca. 70; graue Haare, 177 cm, braune Augen",
				"triage": "-",
				"mobility": "initial bettl\u00e4gerig",
				"preexistingIllnesses": "Hypertonie; KHK",
				"permanentMedication": "\u00df-Blocker; Diuretikum:",
				"currentCaseHistory": "v. 3 Wo. Chemo nach ColonCA begonnen, jetzt ANV; gestern auf Normalstation Lungen\u00f6dem entwickelt, nach 4 Stunden CPAP wieder oB.; n\u00e4chste Dialyse morgen",
				"pretreatment": "1xZugang, ZVK, 1xVEL, Antikoagulanz, KatecholaminP, DiuretikumP, Sauerstoff,"
			}, {
				"code": 1037,
				"personalDetails": "Peter Brummer 10.09.1946 Henkelstr. 1, 40599 D\u00fcsseldorf",
				"injury": "",
				"biometrics": "m\u00e4nnlich; ca. 70; blaue Augen, grauhaarig, Brille 163 cm",
				"triage": "-",
				"mobility": "initial bettl\u00e4gerig",
				"preexistingIllnesses": "Alkoholabusus; mehrfach schon Pankreatitis",
				"permanentMedication": "Distraneurin,",
				"currentCaseHistory": "v. 2 Tagen mit nekrotisierender Pankreatitis aufgenommen; Enzyme leicht r\u00fcckl\u00e4ufig.",
				"pretreatment": "1xZugang, ZVK, 2xVEL, Kortikosteroid, Antikoagulanz, Insulin, Sauerstoff,"
			}, {
				"code": 1038,
				"personalDetails": "Ulrich Hering 25.03.1979 Kruppstr. 57, 40227 D\u00fcsseldorf",
				"injury": "",
				"biometrics": "m\u00e4nnlich; ca. 37; braune Augen, blonde Haare, 174 cm",
				"triage": "-",
				"mobility": "initial bettl\u00e4gerig",
				"preexistingIllnesses": "keine",
				"permanentMedication": "keine Dauermedikation",
				"currentCaseHistory": "v. 2 Tagen mit unklarem Bauchschmerz aufgenommen; Gestern im EKG VES und Salven gehabt; TropT, Leber- und Pankreas-Enzyme oB.",
				"pretreatment": "1xZugang, 1xVEL, Antikoagulanz,"
			}, {
				"code": 1039,
				"personalDetails": "Klaus Zobel 03.07.1940 Westfalenstr. 92, 40472 D\u00fcsseldorf",
				"injury": "Wunde und Drainagen unauff\u00e4llig",
				"biometrics": "m\u00e4nnlich; ca. 76; grauhaarig, blaue Augen, 1,79 m",
				"triage": "-",
				"mobility": "initial bettl\u00e4gerig",
				"preexistingIllnesses": "Herzinsuffizienz; Arthrose; beginnende Demenz",
				"permanentMedication": "Schilddr\u00fcsenhormone; Diuretikum; Digitalis",
				"currentCaseHistory": "gestern OP; TEP-Wechsel H\u00fcfte, viel geblutet, nur Eigenblut und Autotrans bekommen; Hb post OP 7,8",
				"pretreatment": "1xZugang, ZVK, 2xVEL, Antikoagulanz, Sauerstoff,"
			}, {
				"code": 1040,
				"personalDetails": "Heidrun Eisele 06.04.1955 Am Wald 6, 40789 Monheim",
				"injury": "",
				"biometrics": "weiblich; ca. 61; blaue Augen, graue Haare, 1,63 m",
				"triage": "-",
				"mobility": "initial bettl\u00e4gerig",
				"preexistingIllnesses": "AA bei VHF; chronische Hypothyreose; Depressionen; vor 7 Mo. Schlaganfall mit minimalem mentalen Defizit als Residuum",
				"permanentMedication": "Digitalis; Verapamil; Schilddr\u00fcsenhormone; ASS",
				"currentCaseHistory": "gestern LapHemicolektomie bei Divertikulitis; intraoperativ mehrfach hypoton; geringer Blutverlust",
				"pretreatment": "1xZugang, ZVK, 2xVEL, Antikoagulanz, Sauerstoff,"
			}, {
				"code": 1041,
				"personalDetails": "Vera Zwanzig 25.04.1946 S\u00fcrther Str. 92, 50996 K\u00f6ln",
				"injury": "keine",
				"biometrics": "weiblich; ca. 70; braune Haare, braune Augen, 178 cm",
				"triage": "-",
				"mobility": "initial nicht gehf\u00e4hig",
				"preexistingIllnesses": "vor 7 J. Schilddr\u00fcsen- CA; Diab. mell.; Hpertonie",
				"permanentMedication": "\u00df-Blocker, Schilddr\u00fcsenhormon, Metformin, Magnesium",
				"currentCaseHistory": "wird vom Tochter im Rollstuhl gebracht: auf Toilette verwirrt aufgefunden; jetzt zunehmend schlechter geworden.",
				"pretreatment": ""
			}]
		})
	},
	{
		id: 'exercise',
		data: '{"messageType":"exercise","exercise":{"exerciseId":"abcdef","areas":[' +
			'{"areaId":1,"areaName":"Intensiv",' +
				'"patients":[' +
					'{"patientId":"145345","patientName":"Anna Müller","code":1007,"triage":"1"},' +
					'{"patientId":"256443","patientName":"Frank Huber","code":1008,"triage":"1"}' +
				'],' +
				'"personnel":[' +
					'{"personnelId":10,"personnelName":"Sebastian Lieb"},' +
					'{"personnelId":1,"personnelName":"Albert Spahn"}' +
				'],' +
				'"material":[' +
					'{"materialId":1,"materialName":"Beatmungsgerät","materialType":"DE"},' +
					'{"materialId":2,"materialName":"Defibrillator","materialType":"DE"}' +
				']' +
			'},' +
			'{"areaId":2,"areaName":"ZNA",' +
				'"patients":[' +
					'{"patientId":"123456","patientName":"Ludger Göhlke","code":1009,"triage":"1"},' +
					'{"patientId":"623422","patientName":"Friedrich Gerhard","code":1007,"triage":"1"},' +
					'{"patientId":"754262","patientName":"Hans Schmidt","code":1017,"triage":"2"},' +
					'{"patientId":"836545","patientName":"Johannes Müller","code":1018,"triage":"2"},' +
					'{"patientId":"963733","patientName":"Sophie Schneider","code":1019,"triage":"2"},' +
					'{"patientId":"105626","patientName":"Lisa Fischer","code":1020,"triage":"2"},' +
					'{"patientId":"126541","patientName":"Julia Meyer","code":1004,"triage":"3"},' +
					'{"patientId":"526612","patientName":"Max Weber","code":1012,"triage":"3"},' +
					'{"patientId":"256413","patientName":"Lukas Wagner","code":1013,"triage":"3"},' +
					'{"patientId":"145664","patientName":"Laura Becker","code":1014,"triage":"3"},' +
					'{"patientId":"157242","patientName":"Anna Schäfer","code":1015,"triage":"3"}' +
				'],' +
				'"personnel":[' +
					'{"personnelId":11,"personnelName":"Hannah Mayer"},' +
					'{"personnelId":3,"personnelName":"Jens Schweizer"},' +
					'{"personnelId":2,"personnelName":"Lena Schulze"},' +
					'{"personnelId":7,"personnelName":"Günther Beutle"},' +
					'{"personnelId":8,"personnelName":"Julian Mohn"},' +
					'{"personnelId":9,"personnelName":"Elisabeth Bauer"},' +
					'{"personnelId":12,"personnelName":"Hans Schmidt"},' +
					'{"personnelId":13,"personnelName":"Johannes Müller"},' +
					'{"personnelId":14,"personnelName":"Sophie Schneider"},' +
					'{"personnelId":15,"personnelName":"Lisa Fischer"}' +
				'],' +
				'"material":[' +
					'{"materialId":3,"materialName":"EKG-Maschine","materialType":"DE"},' +
					'{"materialId":4,"materialName":"EKG-Monitor","materialType":"DE"},' +
					'{"materialId":7,"materialName":"Pulsoximeter","materialType":"DE"},' +
					'{"materialId":8,"materialName":"EEG","materialType":"DE"},' +
					'{"materialId":9,"materialName":"Narkosegerät","materialType":"DE"},' +
					'{"materialId":10,"materialName":"Beatmungsgerät","materialType":"DE"},' +
					'{"materialId":11,"materialName":"Defibrillator","materialType":"DE"},' +
					'{"materialId":12,"materialName":"Anästhesiegerät","materialType":"DE"},' +
					'{"materialId":13,"materialName":"Elektrochirurgiegerät","materialType":"DE"},' +
					'{"materialId":14,"materialName":"Herzschrittmacher","materialType":"DE"},' +
					'{"materialId":15,"materialName":"Infusionspumpe","materialType":"DE"},' +
					'{"materialId":16,"materialName":"Patientenmonitor","materialType":"DE"},' +
					'{"materialId":17,"materialName":"Ultraschallgerät","materialType":"DE"},' +
					'{"materialId":18,"materialName":"MRT-Gerät","materialType":"DE"},' +
					'{"materialId":19,"materialName":"Röntgengerät","materialType":"DE"},' +
					'{"materialId":20,"materialName":"CT-Scanner","materialType":"DE"},' +
					'{"materialId":21,"materialName":"Blut AB positiv","materialType":"BL"},' +
					'{"materialId":21,"materialName":"Blut A positiv","materialType":"BL"},' +
					'{"materialId":21,"materialName":"Blut 0 positiv","materialType":"BL"},' +
					'{"materialId":22,"materialName":"Blut 0 negativ","materialType":"BL"}' +
				']' +
			'},' +
			'{"areaId":3,"areaName":"Wagenhalle",' +
				'"patients":[' +
					'{"patientId":"126143","patientName":"Isabelle Busch","code":1020,"triage":"3"},' +
					'{"patientId":"462455","patientName":"Jasper Park","code":1016,"triage":"2"}' +
				'],' +
				'"personnel":[' +
					'{"personnelId":5,"personnelName":"Finn Heizmann"},' +
					'{"personnelId":6,"personnelName":"Ursula Seiler"}' +
				'],' +
				'"material":[' +
					'{"materialId":5,"materialName":"EKG-Gerät","materialType":"DE"},' +
					'{"materialId":6,"materialName":"Blutdruckmessgerät","materialType":"DE"},' +
					'{"materialId":23,"materialName":"Blut A negativ","materialType":"BL"},' +
					'{"materialId":24,"materialName":"Blut A positiv","materialType":"BL"}' +
				']' +
			'}' +
		']}}'
	},
	{id: 'exercise-start', data: '{"messageType":"exercise-start"}'},
	{id: 'exercise-pause', data: '{"messageType":"exercise-pause"}'},
	{id: 'exercise-resume', data: '{"messageType":"exercise-resume"}'},
	{id: 'exercise-end', data: '{"messageType":"exercise-end"}'},
]