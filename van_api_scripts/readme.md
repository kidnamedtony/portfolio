# VAN API Scripts
In this folder, you'll find a lightly redacted version of the "Turf List Number Getter" script, which is a script I built to pull turf packet numbers from VAN.

Okay, that was a lot of jargon. What's it all mean?
- Turf: turf is a map area of voters that our data has identified are worth reaching out to by knocking on their doors and talking to them, whether it's to try and persuade them to vote for a particular candidate, to create a plan to get out and vote by or before election day, etc. Campaigns get this voter data from their state's secretary of state, and Organizers "cut turf"--these map areas--for volunteers to "canvass", or knock on their doors to speak to these voters.
- VAN: Voter Activation Network, or VAN, is a database and campaign management tool (kinda' like a CRM) in political organizing, used primarily by progressive organizations and campaigns. It helps track voter and volunteer data, manage outreach efforts, and analyze engagement to optimize campaign strategies like door-knocking, phonebanking, and event organizing. Organizers "cut" the aforementioned turf in VAN, and volunteers use a mobile version of VAN to access those turfs to knock on doors, for example.
- Turf List Number: Each turf, once it's been created or "cut" by an Organizer, gets a unique ID number. This number is necessary for volunteers to input into the mobile version of VAN so they can access the turf map (complete with voter data like their name and address) to knock on doors and speak to voters.

Typically, Organizers would print a list of these turf numbers to give to their many volunteers. That's a lot of paper! And, printing these numbers typically do not make tracking door-knocking progress at the various levels--from field office to regional to state--particularly easy.

That's where this script comes in, which not only pulls these turf list numbers from VAN's API, it also pulls additional data like the turf's author (i.e., who cut it?), when they created it, how many people and doors are associated with each turf, etc., dumping all that data into a Google Sheet dedicated to reporting for leadership and Organizing directors, as well as providing easy access of the turf list numbers to Organizers and volunteers.