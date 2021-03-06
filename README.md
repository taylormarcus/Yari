# Y.A.R.I - "Yet Another RPG Implement"


> "Yari is the term for a traditionally-made Japanese blade in the form of a spear, or more specifically, the straight-headed spear. - From [Wikipedia](http://www.wikipedia.org), the free encyclopedia


#### DESCRIPTION

Yari generates 5th edition Dungeons & Dragons characters. Currently, Yari supports content from the following rulebooks: 

  * *Player's Handbook*
  * *Mordenkainen's Tome of Foes*
  * *Volo's Guide to Monsters*
  * *Xanatar's Guide to Everything*

Planning to eventually incorporate content from *Tasha's Cauldron of Everything*.


#### REQUIREMENTS
  
  * aiohttp
  * beautifulsoup4
  * click
  * PyYAML


#### INSTALLATION

To install Yari directly from Github (usually the latest version):

```pip install git+git://github.com/taylormarcus/Yari``` or ```pip3 install git+git://github.com/taylormarcus/Yari```

To install Yari from PYPI, run the following command:

```pip install Yari``` or ```pip3 install Yari```


#### USAGE

```
Usage: yari [OPTIONS]

Options:
  -race TEXT        Character's chosen race. Available races are: Aasimar,
                    Bugbear, Dragonborn, Dwarf, Elf, Firbolg, Gith, Gnome,
                    Goblin, Goliath, HalfElf, HalfOrc, Halfling, Hobgoblin,
                    Human, Kenku, Kobold, Lizardfolk, Orc, Tabaxi, Tiefling,
                    Triton and Yuanti. Default value is 'Human'.

  -subrace TEXT     Character's chosen subrace. Available subraces are based
                    upon the chosen race: Aasimar (Fallen, Protector,
                    Scourge), Dwarf (Duergar, Hill, Mountain), Elf (Drow,
                    Eladrin, High, Sea, Shadar-kai, Wood), Gith (Githyanki,
                    Githzerai), Gnome (Deep, Forest, Rock), Halfling
                    (Lightfoot, Stout), Tiefling (Asmodeus, Baalzebub,
                    Dispater, Fierna, Glasya, Levistus, Mammon,
                    Mephistopheles, Zariel).

  -sex TEXT         Character's chosen gender.
  -alignment TEXT   Character's chosen alignment. Available alignments are: CE
                    (Chaotic Evil), CG (Chaotic Good), CN (Chaotic Neutral),
                    LE (Lawful Evil), LG (Lawful Good), LN (Lawful Neutral),
                    NE (Neutral Evil), NG (Neutral Good), N (True Neutral).
                    Default value is 'N'.

  -background TEXT  Character's chosen background. Available backgrounds are:
                    Acolyte, Charlatan, Criminal, Entertainer, Folk Hero,
                    Guild Artisan, Hermit, Noble, Outlander, Sage, Sailor,
                    Soldier, Urchin. Default value depends on class: Barbarian 
                    (Outlander), Bard (Entertainer), Cleric (Acolyte), Druid 
                    (Hermit), Fighter (Soldier), Monk (Hermit), Paladin (Noble),
                    Ranger (Outlander), Rogue (Charlatan), Sorcerer (Hermit), 
                    Warlock (Charlatan), and Wizard (Sage).

  -klass TEXT       Character's chosen class. Available classes are:
                    Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin,
                    Ranger, Rogue, Sorcerer, Warlock, and Wizard. Default
                    value is 'Fighter'.

  -subclass TEXT    Character's chosen subclass (archetype, domain, path,
                    etc). Available subclasses are based upon the chosen
                    class: Barbarian (Path of the Ancestral Guardian, Path of
                    the Berserker, Path of the Storm Herald, Path of the Totem
                    Warrior, Path of the Zealot), Bard (College of Glamour,
                    College of Lore, College of Swords, College of Valor,
                    College of Whispers), Cleric (Forge Domain, Grave Domain,
                    Knowledge Domain, Life Domain, Light Domain, Nature
                    Domain, Tempest Domain, Trickery Domain, War Domain),
                    Druid (Circle of the Arctic, Circle of the Coast, Circle
                    of the Desert, Circle of Dreams, Circle of the Forest,
                    Circle of the Grassland, Circle of the Moon, Circle of the
                    Mountain, Circle of the Shepherd, Circle of the Swamp,
                    Circle of the Underdark), Fighter (Arcane Archer, Battle
                    Master, Cavalier, Champion, Eldritch Knight, Samurai),
                    Monk (Way of Shadow, Way of the Drunken Master, Way of the
                    Four Elements, Way of the Kensei, Way of the Open Hand,
                    Way of the Sun Soul), Paladin (Oath of the Ancients, Oath
                    of Conquests, Oath of Devotion, Oath of Redemption, Oath
                    of Vengeance), Ranger (Beast Master, Gloom Stalker,
                    Horizon Walker, Hunter, Monster Slayer), Rogue (Arcane
                    Trickster, Assassin, Inquisitive, Mastermind, Scout,
                    Swashbuckler, Thief), Sorcerer (Divine Soul, Draconic
                    Bloodline, Shadow Magic, Storm Sorcery, Wild Magic),
                    Warlock (The Archfey, The Celestial, The Fiend, The Great
                    Old One, The Hexblade), and Wizard (School of Abjuration,
                    School of Conjuration, School of Divination, School of
                    Enchantment, School of Evocation, School of Illusion,
                    School of Necromancy, School of Transmutation, War Magic).

  -level INTEGER    Character's class level. Must be between 1-20. Default
                    value is 1.

  -ratio INTEGER    Character's 'ability to feat' upgrade ratio. Must be
                    between 0-10. This value will determine the percentage of
                    level upgrades allocated to the character's ability
                    scores. The difference between this value from 100 will
                    then be allocated to the percentage of chosen feats (i.e:
                    So if this value is 2 or 20%, 80 percent will
                    automatically be allocated to feats). Default value is 5.

  -port INTEGER     Character server's chosen port. Default value is 8080.
  --version         Show the version and exit.
  --help            Show this message and exit.
```

To run Yari with minimal arguments, type the following in your terminal:

    yari

If Yari is run with just the bare minimum arguments as shown above, a character will be generated using the previously mentioned default values where applicable and randomly generate those values that have no defined defaults.

Here's a more complex example:

    yari -race=Dragonborn -sex=Female -alignment=LG -klass=Paladin -level=10

If you haven't already noticed, this would generate a 10th level female Dragonborn Paladin with a Lawful Good alignment.

Here's an example of some general Yari output.

    ▶ yari -race=Dragonborn -level=10
    INFO: Result of 16 assigned to ability 'Dexterity'.
    INFO: Result of 12 assigned to ability 'Constitution'.
    INFO: Result of 11 assigned to ability 'Wisdom'.
    INFO: Result of 10 assigned to ability 'Intelligence'.
    INFO: Result of 8 assigned to ability 'Charisma'.
    INFO: Result of 11 assigned to ability 'Strength'.
    INFO: Bonus of 2 applied to 'Strength'. Score is now 13.
    INFO: Bonus of 1 applied to 'Charisma'. Score is now 9.
    INFO: Checking prerequisites for 'Second Chance'...
    WARN: Prerequisites not met for 'Second Chance'.
    INFO: Checking prerequisites for 'Spell Sniper'...
    WARN: Prerequisites not met for 'Spell Sniper'.
    INFO: Checking prerequisites for 'Squat Nimbleness'...
    WARN: Prerequisites not met for 'Squat Nimbleness'.
    INFO: Checking prerequisites for 'Weapon Master'...
    WARN: Prerequisites not met for 'Weapon Master'.
    INFO: Checking prerequisites for 'Fey Teleportation'...
    WARN: Prerequisites not met for 'Fey Teleportation'.
    INFO: Checking prerequisites for 'Dragon Hide'...
    OK: Prerequisites met for 'Dragon Hide'.
    INFO: Checking prerequisites for 'Observant'...
    OK: Prerequisites met for 'Observant'.
    ======== Running on http://127.0.0.1:8080 ========
    (Press CTRL+C to quit)


#### DISCLAIMER

This software is not affiliated with, endorsed, sponsored, or specifically approved
by Wizards of the Coast LLC. This software is a fan made tool.
