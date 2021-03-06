import math
import random
import sys

from .constants import (
    PC_BACKGROUNDS,
    PC_CLASSES,
    PC_LANGUAGES,
    PC_SKILLS,
    PC_SUBRACES,
)
from .dice import roll
from .sourcereader import Load


class _AttributeBuilder:
    """
    DO NOT call class directly. Used to generate ability attributes.

    Inherited by the following classes:

        - Charisma
        - Constitution
        - Dexterity
        - Intelligence
        - Strength
        - Wisdom

    :param int score: The value of the specified ability score.
    :param list skills: The character's skill list.

    """

    def __init__(self, score: int, skills: list) -> None:
        self.attribute = self.__class__.__name__
        if self.attribute == "_Attributes":
            raise Exception(
                "This class must be inherited to use. It is currently used by "
                "the Charisma, Constitution, Dexterity, Intelligence, Strength, "
                "and Wisdom 'attribute' classes."
            )

        self.score = score
        self.attr = dict()
        self.attr["value"] = score
        self.attr["modifier"] = get_ability_modifier(self.attr.get("value"))
        self.attr["ability_checks"] = self.attr.get("modifier")
        self.attr["name"] = self.attribute
        self.attr["saving_throws"] = self.attr.get("modifier")
        self.attr["skills"] = dict()

        # Get skills associated with this attribute
        attribute_skills = [x for x in self._get_skills_by_attribute()]
        # Get the ability modifier for the associated attribute
        for skill in skills:
            if skill in attribute_skills:
                self.attr["skills"].update({skill: get_ability_modifier(score)})

    def __repr__(self):
        return '<{} score="{}">'.format(self.attribute, self.score)

    def _get_skills_by_attribute(self):
        """Returns a skill list by attribute."""
        for skill in PC_SKILLS:
            attribute = Load.get_columns(skill, "ability", source_file="skills")
            if attribute == self.attribute:
                yield skill


class Charisma(_AttributeBuilder):
    def __init__(self, score: int, skills: list) -> None:
        super(Charisma, self).__init__(score, skills)


class Constitution(_AttributeBuilder):
    def __init__(self, score: int, skills: list) -> None:
        super(Constitution, self).__init__(score, skills)


class Dexterity(_AttributeBuilder):
    def __init__(self, score: int, skills: list) -> None:
        super(Dexterity, self).__init__(score, skills)


class Intelligence(_AttributeBuilder):
    def __init__(self, score: int, skills: list) -> None:
        super(Intelligence, self).__init__(score, skills)


class Strength(_AttributeBuilder):
    def __init__(self, score: int, skills: list) -> None:
        super(Strength, self).__init__(score, skills)
        self.attr["carry_capacity"] = score * 15
        self.attr["push_pull_carry"] = self.attr.get("carry_capacity") * 2
        self.attr["maximum_lift"] = self.attr.get("push_pull_carry")


class Wisdom(_AttributeBuilder):
    def __init__(self, score: int, skills: list) -> None:
        super(Wisdom, self).__init__(score, skills)


def get_ability_modifier(score: int) -> int:
    """
    Returns ability modifier by score.

    :param int score: Score to calculate modifier for.

    """
    return score != 0 and int((score - 10) / 2) or 0


class _ClassBuilder:
    """
    DO NOT call class directly. Used to generate class features.

    Inherited by the following classes:

        - Barbarian
        - Bard
        - Cleric
        - Druid
        - Fighter
        - Monk
        - Paladin
        - Ranger
        - Rogue
        - Sorcerer
        - Warlock
        - Wizard

    :param str subclass: Character's chosen subclass.
    :param str background: Character's chosen background.
    :param int level: Character's chosen level.
    :param list race_skills: Character's bonus racial skills (if applicable).

    """

    def __init__(
        self, subclass: str, background: str, level: int, race_skills: list
    ) -> None:
        self.klass = self.__class__.__name__
        if self.klass == "_Classes":
            raise Exception(
                "This class must be inherited to use. It is currently used by "
                "the Barbarian, Bard, Cleric, Druid, Fighter, Monk, Paladin, "
                "Ranger, Rogue, Sorcerer, Warlock and Wizard 'job' classes."
            )

        if not get_is_class(self.klass):
            raise ValueError(f"Character class '{self.klass}' is invalid.")

        if not isinstance(level, int):
            raise ValueError("Argument 'level' value must be of type 'int'.")
        elif level not in range(1, 21):
            raise ValueError("Argument 'level' value must be between 1-20.")
        else:
            self.level = level

        if self.level >= 3:
            if get_is_subclass(subclass, self.klass):
                self.subclass = subclass
            else:
                raise ValueError(
                    f"Character class '{self.klass}' has no subclass '{subclass}'."
                )
        else:
            self.subclass = ""

        if get_is_background(background):
            self.background = background
        else:
            raise ValueError(f"Character background '{background}' is invalid.")

        if not isinstance(race_skills, list):
            raise ValueError("Argument 'race_skills' value must be a 'list'.")
        else:
            self.race_skills = race_skills

        # Assign base variables
        self.all = None
        self.primary_ability = None
        self.subclasses = None
        self.default_background = None
        self.features = None
        self.hit_die = None
        self.hit_points = None
        self.proficiency_bonus = None
        self.armors = None
        self.tools = None
        self.weapons = None
        self.saving_throws = None
        self.skills = None
        self.magic_class = None
        self.spell_slots = None

    def __repr__(self):
        if self.subclass != "":
            return '<{} subclass="{}" level="{}">'.format(
                self.klass, self.subclass, self.level
            )
        else:
            return '<{} level="{}">'.format(self.klass, self.level)

    def _add_abilities(self) -> None:
        """
        Generates primary abilities by character class.

        Classes with multiple primary ability choices will select one.

            - Fighter: Strength|Dexterity
            - Fighter: Constitution|Intelligence
            - Ranger: Dexterity|Strength
            - Rogue: Charisma|Intelligence
            - Wizard: Constitution|Dexterity

        """
        class_abilities = Load.get_columns(
            self.klass, "abilities", source_file="classes"
        )
        if self.klass == "Cleric":
            class_abilities[2] = random.choice(class_abilities[2])
        elif self.klass in ("Fighter", "Ranger"):
            ability_choices = class_abilities.get(1)
            class_abilities[1] = random.choice(ability_choices)
            if self.klass == "Fighter" and self.subclass != "Eldritch Knight":
                class_abilities[2] = "Constitution"
            elif self.klass == "Fighter" and self.subclass == "Eldritch Knight":
                class_abilities[2] = "Intelligence"
            else:
                class_abilities[2] = class_abilities.get(2)
        elif self.klass == "Rogue":
            if self.subclass != "Arcane Trickster":
                class_abilities[2] = "Charisma"
            else:
                class_abilities[2] = "Intelligence"
        elif self.klass == "Wizard":
            ability_choices = class_abilities.get(2)
            class_abilities[2] = random.choice(ability_choices)

        self.all["abilities"] = class_abilities

    def _add_equipment(self) -> None:
        """Generates a list of starting equipment by class & background."""
        class_equipment = Load.get_columns(
            self.klass, "equipment", source_file="classes"
        )
        background_equipment = Load.get_columns(
            self.background, "equipment", source_file="backgrounds"
        )
        equipment = class_equipment + background_equipment
        equipment.sort()
        self.all["equipment"] = self.equipment = equipment

    def _add_features(self) -> None:
        """Generates a collection of class and subclass features by level."""

        def feature_splice(cls_features: dict, sc_features: dict) -> dict:
            """Splices class/subclass features."""
            for lv, ft in sc_features.items():
                if lv in cls_features:
                    feature_list = cls_features[lv] + sc_features[lv]
                    feature_list.sort()
                    cls_features[lv] = feature_list
                else:
                    cls_features[lv] = sc_features[lv]
            return cls_features

        try:
            class_features = Load.get_columns(
                self.klass, "features", source_file="classes"
            )
            if self.subclass != "":
                subclass_features = Load.get_columns(
                    self.subclass, "features", source_file="subclasses"
                )
                features = feature_splice(class_features, subclass_features)
            else:
                features = class_features
            # Create feature dictionary based on level.
            features = {lv: features[lv] for lv in features if lv <= self.level}
        except (TypeError, KeyError) as e:
            # exit("Cannot find class/subclass '{}'")
            sys.exit(e)
        else:
            for lv, fts in features.items():
                features[lv] = tuple(fts)
            self.all["features"] = features

    def _add_hit_die(self) -> None:
        """Generates hit die and point totals."""
        hit_die = self.all.get("hit_die")
        self.all["hit_die"] = f"{self.level}d{hit_die}"
        self.all["hit_points"] = hit_die
        if self.level > 1:
            new_level = self.level - 1
            die_rolls = list()
            for _ in range(0, new_level):
                hp_result = int((hit_die / 2) + 1)
                die_rolls.append(hp_result)
            self.all["hit_points"] += sum(die_rolls)

    def _add_extended_magic(self) -> None:
        """Adds extended magic spells (Domain, Warlock, etc)."""
        self.all["magic_class"] = dict()

        # If no extended magic available
        if self.subclass == "" or not has_extended_magic(self.subclass):
            return

        extended_magic_list = dict()
        # Only apply spells available at that level
        for level, spells in Load.get_columns(
            self.subclass, "magic", source_file="subclasses"
        ).items():
            if level <= self.level:
                extended_magic_list[level] = tuple(spells)

        self.all["magic_class"] = extended_magic_list

    def _add_proficiencies(self) -> None:
        """Merge class proficiencies with subclass proficiencies (if applicable)."""
        # If no subclass is specified
        if self.subclass == "":
            return

        # If no bonus proficiency available
        bonus_proficiency = self.all.get("proficiency")
        if bonus_proficiency is None:
            return

        for category in ("Armor", "Tools", "Weapons"):
            for index, proficiency in enumerate(bonus_proficiency):
                if category in proficiency:
                    if (
                        category
                        in (
                            "Armor",
                            "Weapons",
                        )
                        and self.subclass in ("College of Valor", "College of Swords")
                        and self.level < 3
                    ):
                        return
                    elif (
                        category == "Tools"
                        and self.subclass == "Assassin"
                        and self.level < 3
                    ):
                        return

                    try:
                        subclass_proficiency = [
                            x for x in get_subclass_proficiency(self.subclass, category)
                        ]
                        proficiencies = proficiency[1] + subclass_proficiency[0]
                        self.all["proficiency"][index] = [category, proficiencies]
                    except IndexError:
                        pass

        # Monk bonus tool or musical instrument proficiency.
        if self.klass == "Monk":
            tool_selection = [random.choice(self.all["proficiency"][1][1])]
            self.all["proficiency"][1][1] = tool_selection

        self.all["proficiency"] = [tuple(x) for x in self.all.get("proficiency")]

    def _add_skills(self):
        """Generates character's skill set."""
        # Skill handling and allotment.
        skill_pool = self.all["proficiency"][4][1]
        skills = list()

        # Get skill allotment by class.
        if self.klass in ("Rogue",):
            allotment = 4
        elif self.klass in ("Bard", "Ranger"):
            allotment = 3
        else:
            allotment = 2

        # Remove any bonus racial skill from pool.
        if len(self.race_skills) != 0:
            skill_pool = [x for x in skill_pool if x not in self.race_skills]
            skills = skills + self.race_skills

        skills = skills + random.sample(skill_pool, allotment)
        skills.sort()
        self.all["proficiency"][4] = ["Skills", skills]

        # Proficiency handling and allotment (if applicable).
        self.all["proficiency_bonus"] = get_proficiency_bonus(self.level)

    def _add_spell_slots(self):
        """Generates character's spell slots."""
        spell_slots = self.all.get("spell_slots")
        # Class has no spellcasting ability
        if spell_slots is None:
            self.all["spell_slots"] = "0"
        # Class has spellcasting ability
        else:
            # Non spellcasting Fighter/Rogue
            if self.klass in ("Fighter", "Rogue") and self.subclass not in (
                "Arcane Trickster",
                "Eldritch Knight",
            ):
                spell_slots = "0"
            else:
                spell_slots = spell_slots.get(self.level)
            self.all["spell_slots"] = spell_slots

    def create(self) -> None:
        # Load class template
        self.all = Load.get_columns(self.klass, source_file="classes")
        # Generate class fine-tuning modifications
        self._add_abilities()
        self._add_equipment()
        self._add_features()
        self._add_hit_die()
        self._add_extended_magic()
        self._add_proficiencies()
        self._add_skills()
        self._add_spell_slots()
        # Apply class fine-tuning modifications
        self.primary_ability = self.all.get("abilities")
        self.subclasses = self.all.get("subclasses")
        self.default_background = self.all.get("background")
        self.features = self.all.get("features")
        self.hit_die = self.all.get("hit_die")
        self.hit_points = self.all.get("hit_points")
        self.proficiency_bonus = self.all.get("proficiency_bonus")
        self.armors = self.all.get("proficiency")[0][1]
        self.tools = self.all.get("proficiency")[1][1]
        self.weapons = self.all.get("proficiency")[2][1]
        self.saving_throws = self.all.get("proficiency")[3][1]
        self.skills = self.all.get("proficiency")[4][1]
        self.magic_class = self.all["magic_class"]
        self.spell_slots = self.all.get("spell_slots")
        # Delete class template
        del self.all


class Barbarian(_ClassBuilder):
    def __init__(self, subclass, background, level, race_skills) -> None:
        super(Barbarian, self).__init__(subclass, background, level, race_skills)


class Bard(_ClassBuilder):
    def __init__(self, subclass, background, level, race_skills) -> None:
        super(Bard, self).__init__(subclass, background, level, race_skills)


class Cleric(_ClassBuilder):
    def __init__(self, subclass, background, level, race_skills) -> None:
        super(Cleric, self).__init__(subclass, background, level, race_skills)


class Druid(_ClassBuilder):
    def __init__(self, subclass, background, level, race_skills) -> None:
        super(Druid, self).__init__(subclass, background, level, race_skills)


class Fighter(_ClassBuilder):
    def __init__(self, subclass, background, level, race_skills) -> None:
        super(Fighter, self).__init__(subclass, background, level, race_skills)


class Monk(_ClassBuilder):
    def __init__(self, subclass, background, level, race_skills) -> None:
        super(Monk, self).__init__(subclass, background, level, race_skills)


class Paladin(_ClassBuilder):
    def __init__(self, subclass, background, level, race_skills) -> None:
        super(Paladin, self).__init__(subclass, background, level, race_skills)


class Ranger(_ClassBuilder):
    def __init__(self, subclass, background, level, race_skills) -> None:
        super(Ranger, self).__init__(subclass, background, level, race_skills)


class Rogue(_ClassBuilder):
    def __init__(self, subclass, background, level, race_skills) -> None:
        super(Rogue, self).__init__(subclass, background, level, race_skills)


class Sorcerer(_ClassBuilder):
    def __init__(self, subclass, background, level, race_skills) -> None:
        super(Sorcerer, self).__init__(subclass, background, level, race_skills)


class Warlock(_ClassBuilder):
    def __init__(self, subclass, background, level, race_skills) -> None:
        super(Warlock, self).__init__(subclass, background, level, race_skills)


class Wizard(_ClassBuilder):
    def __init__(self, subclass, background, level, race_skills) -> None:
        super(Wizard, self).__init__(subclass, background, level, race_skills)


def get_default_background(klass: str):
    """
    Returns the default background by klass.

    :param str klass: Characters chosen class.

    """
    return Load.get_columns(klass, "background", source_file="classes")


def get_is_background(background: str) -> bool:
    """
    Returns whether the background is valid.

    :param str background: Chosen background to check.

    """
    return background in PC_BACKGROUNDS


def get_is_class(klass: str) -> bool:
    """
    Returns whether the klass is valid.

    :param str klass: Character's chosen class.

    """
    return klass in PC_CLASSES


def get_is_subclass(subclass: str, klass: str) -> bool:
    """
    Returns whether subclass is a valid subclass of klass.

    :param str subclass: Character's chosen subclass.
    :param str klass: Character's chosen class.

    """
    return subclass in Load.get_columns(klass, "subclasses", source_file="classes")


def get_subclass_proficiency(subclass: str, category: str):
    """
    Returns subclass bonus proficiencies (if ANY).

    :param str subclass: Character subclass to get proficiencies for.
    :param str category: Proficiency category to get proficiencies for.

    """
    if category not in ("Armor", "Tools", "Weapons"):
        raise ValueError("Argument 'category' must be 'Armor', 'Tools' or 'Weapons'.")

    trait_list = Load.get_columns(subclass, source_file="subclasses")
    if trait_list.get("proficiency") is not None:
        proficiencies = trait_list.get("proficiency")
        for proficiency in proficiencies:
            if proficiency[0] == category:
                yield proficiency[1]


def get_all_languages() -> tuple:
    return PC_LANGUAGES


def get_all_skills() -> tuple:
    """Returns a list of ALL skills."""
    return PC_SKILLS


def get_background_skills(background: str):
    """
    Returns bonus skills by background (if applicable).

    :param str background: Background to return background skills for.

    """
    return Load.get_columns(background, "skills", source_file="backgrounds")


def get_subclasses_by_class(klass: str) -> tuple:
    """
    Returns a tuple of valid subclasses for klass.

    :param str klass: Character's class.

    """
    return Load.get_columns(klass, "subclasses", source_file="classes")


def get_proficiency_bonus(level: int) -> int:
    """
    Returns a proficiency bonus value by level.

    :param int level: Level of character.

    """
    return math.ceil((level / 4) + 1)


def has_extended_magic(subclass: str) -> bool:
    """
    Returns whether class subclass has spells.

    :param str subclass: Character's subclass.

    """
    if Load.get_columns(subclass, "magic", source_file="subclasses") is not None:
        return True
    return False


class _RaceBuilder:
    """
    DO NOT call class directly. Used to generate racial traits.

    Inherited by the following classes:

        - Aasimar
        - Bugbear
        - Dragonborn
        - Dwarf
        - Elf
        - Firbolg
        - Gith
        - Gnome
        - Goblin
        - Goliath
        - HalfElf
        - HalfOrc
        - Halfling
        - Hobgoblin
        - Human
        - Kenku
        - Kobold
        - Lizardfolk
        - Orc
        - Tabaxi
        - Tiefling
        - Triton
        - Yuan-ti

    :param str sex: Character's chosen gender.
    :param str subrace: Character's chosen subrace (if applicable).
    :param int level: Character's chosen level.

    """

    def __init__(self, sex: str, subrace: str = "", level: int = 1) -> None:
        self.race = self.__class__.__name__
        valid_subraces = [sr for sr in get_subraces_by_race(self.race)]

        if self.race == "_Races":
            raise Exception(
                "This class must be inherited to use. It is currently used by "
                "the Aasimar, Bugbear, Dragonborn, Dwarf, Elf, Firbolg, Gith, "
                "Gnome, Goblin, Goliath, HalfElf, HalfOrc, Halfling, Hobgoblin, "
                "Human, Kenku, Kobold, Lizardfolk, Orc, Tabaxi, Tiefling, "
                "Triton, and Yuanti 'race' classes."
            )

        if sex in (
            "Female",
            "Male",
        ):
            self.sex = sex
        else:
            raise ValueError(f"Argument 'sex' value must be 'Male' or 'Female'.")

        if not has_subraces(self.race):
            self.subrace = ""
        else:
            if subrace not in valid_subraces:
                raise ValueError(
                    f"Argument 'subrace' value '{subrace}' is invalid for '{self.race}'."
                )
            elif len(valid_subraces) != 0 and subrace == "":
                raise ValueError(f"Argument 'subrace' is required for '{self.race}'.")
            else:
                self.subrace = subrace

        if not isinstance(level, int):
            raise ValueError("Argument 'level' value must be of type 'int'.")
        else:
            self.level = level

    def __repr__(self):
        if self.subrace != "":
            return '<{} subrace="{}" sex="{}" level="{}">'.format(
                self.race, self.subrace, self.sex, self.level
            )
        else:
            return '<{} sex="{}" level="{}">'.format(self.race, self.sex, self.level)

    def _add_ability_bonus(self):
        """Adds Half-Elves chosen bonus racial ability bonus (if applicable)."""
        if self.race == "HalfElf":
            valid_abilities = [
                "Strength",
                "Dexterity",
                "Constitution",
                "Intelligence",
                "Wisdom",
            ]
            valid_abilities = random.sample(valid_abilities, 2)
            for ability in valid_abilities:
                self.all["bonus"][ability] = 1

    def _add_mass(self) -> None:
        """Generates and sets character's height & weight."""
        height_base = self.all.get("ratio").get("height").get("base")
        height_modifier = self.all.get("ratio").get("height").get("modifier")
        height_modifier = sum(list(roll(height_modifier)))
        self.height = height_base + height_modifier

        weight_base = self.all.get("ratio").get("weight").get("base")
        weight_modifier = self.all.get("ratio").get("weight").get("modifier")
        weight_modifier = sum(list(roll(weight_modifier)))
        self.weight = (height_modifier * weight_modifier) + weight_base

    def _add_traits(self):
        """
        Add all bonus armor, tool, and/or weapon proficiencies, and other traits.

        """
        # Set default attribute values
        self.all = Load.get_columns(self.race, source_file="races")
        self.ancestor = (
            self.race == "Dragonborn"
            and random.choice(
                (
                    "Black",
                    "Blue",
                    "Brass",
                    "Bronze",
                    "Copper",
                    "Gold",
                    "Green",
                    "Red",
                    "Silver",
                    "White",
                )
            )
            or None
        )
        self.bonus = self.all.get("bonus")
        self.darkvision = 0
        self.languages = self.all.get("languages")
        self.magic_innate = list()
        self.ratio = self.all.get("ratio")
        self.size = self.all.get("size")
        self.traits = list()
        self.resistances = list()

        self.skills = list()
        self.armors = list()
        self.tools = list()
        self.weapons = list()

        for trait in self.all.get("traits"):
            if len(trait) == 1:
                if trait[0] not in (
                    "Breath Weapon",
                    "Damage Resistance",
                    "Draconic Ancestry",
                ):
                    self.traits.append(trait[0])
                else:
                    if trait[0] in ("Breath Weapon", "Damage Resistance"):
                        if self.ancestor in (
                            "Black",
                            "Copper",
                        ):
                            self.resistances.append("Acid")
                        elif self.ancestor in (
                            "Blue",
                            "Bronze",
                        ):
                            self.resistances.append("Lightning")
                        elif self.ancestor in (
                            "Brass",
                            "Gold",
                            "Red",
                        ):
                            self.resistances.append("Fire")
                        elif self.ancestor == "Green":
                            self.resistances.append("Poison")
                        elif self.ancestor in ("Silver", "White"):
                            self.resistances.append("Cold")
                        self.traits.append(f"{trait[0]} ({self.resistances[-1]})")
                    else:
                        self.traits.append(f"{trait[0]} ({self.ancestor})")
            else:
                (name, value) = trait
                self.traits.append(name)
                if name == "Darkvision":
                    if self.darkvision == 0:
                        self.darkvision = value
                elif name == "Superior Darkvision":
                    if value > self.darkvision:
                        self.darkvision = value
                elif name == "Cantrip":
                    self.magic_innate = random.sample(value, 1)
                elif name == "Natural Illusionist":
                    self.magic_innate = [value]
                elif name in (
                    "Drow Magic",
                    "Duergar Magic",
                    "Githyanki Psionics",
                    "Githzerai Psionics",
                    "Infernal Legacy",
                    "Innate Spellcasting",
                    "Legacy of Avernus",
                    "Legacy of Cania",
                    "Legacy of Dis",
                    "Legacy of Maladomini",
                    "Legacy of Malbolge",
                    "Legacy of Minauros",
                    "Legacy of Phlegethos",
                    "Legacy of Stygia",
                ):
                    self.magic_innate = [spell[1] for spell in value]
                elif (
                    name in ("Necrotic Shroud", "Radiant Consumption", "Radiant Soul")
                    and self.level >= 3
                ):
                    self.traits.append(name)
                elif name in (
                    "Celestial Resistance",
                    "Duergar Resilience",
                    "Dwarven Resilience",
                    "Fey Ancestry",
                    "Stout Resilience",
                ):
                    self.resistances = self.resistances + value
                elif name in (
                    "Cat's Talent",
                    "Keen Senses",
                    "Menacing",
                    "Natural Athlete",
                    "Sneaky",
                ):
                    self.skills.append(value[0])
                elif name in ("Decadent Mastery", "Extra Language", "Languages"):
                    self.languages.append(random.choice(value))
                elif name in ("Hunter's Lore", "Kenku Training", "Skill Versatility"):
                    self.skills = self.skills + random.sample(value, 2)
                elif name in (
                    "Dwarven Armor Training",
                    "Martial Prodigy (Armor)",
                    "Martial Training (Armor)",
                ):
                    self.armors = value
                elif name == "Tinker":
                    self.tools.append(value)
                elif name == "Tool Proficiency":
                    self.tools.append(random.choice(value))
                elif name in (
                    "Drow Weapon Training",
                    "Dwarven Combat Training",
                    "Elf Weapon Training",
                    "Martial Prodigy (Weapon)",
                    "Sea Elf Training",
                ):
                    self.weapons = value
                elif name in "Martial Training (Weapon)":
                    self.weapons = random.sample(value, 2)

    def _add_subrace_traits(self) -> None:
        """ Merges subrace traits with race traits. """
        # Ignore if no subrace specified
        if self.subrace == "":
            return

        # Load subrace traits
        subrace_traits = Load.get_columns(self.subrace, source_file="subraces")
        # Attempt to merge traits
        for trait, value in subrace_traits.items():
            if trait not in self.all:
                self.all[trait] = subrace_traits[trait]
            elif trait == "bonus":
                for ability, bonus in value.items():
                    self.all[trait][ability] = bonus
            elif trait == "ratio":
                ratio = subrace_traits.get(trait)
                if ratio is not None:
                    self.all[trait] = ratio
            elif trait == "traits":
                for other in subrace_traits.get(trait):
                    self.all[trait].append(other)
        # Updates attributes w/ merged trait values
        self.bonus = self.all.get("bonus")
        self.languages = self.all.get("languages")

    def create(self) -> None:
        """Generates the character's basic racial attributes."""
        self._add_traits()
        self._add_subrace_traits()
        self._add_ability_bonus()
        self._add_mass()
        del self.all


class Aasimar(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Aasimar, self).__init__(sex, subrace, level)


class Bugbear(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Bugbear, self).__init__(sex, subrace, level)


class Dragonborn(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Dragonborn, self).__init__(sex, subrace, level)


class Dwarf(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Dwarf, self).__init__(sex, subrace, level)


class Elf(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Elf, self).__init__(sex, subrace, level)


class Firbolg(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Firbolg, self).__init__(sex, subrace, level)


class Gith(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Gith, self).__init__(sex, subrace, level)


class Gnome(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Gnome, self).__init__(sex, subrace, level)


class Goblin(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Goblin, self).__init__(sex, subrace, level)


class Goliath(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Goliath, self).__init__(sex, subrace, level)


class HalfElf(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(HalfElf, self).__init__(sex, subrace, level)


class HalfOrc(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(HalfOrc, self).__init__(sex, subrace, level)


class Halfling(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Halfling, self).__init__(sex, subrace, level)


class Hobgoblin(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Hobgoblin, self).__init__(sex, subrace, level)


class Human(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Human, self).__init__(sex, subrace, level)


class Kenku(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Kenku, self).__init__(sex, subrace, level)


class Kobold(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Kobold, self).__init__(sex, subrace, level)


class Lizardfolk(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Lizardfolk, self).__init__(sex, subrace, level)


class Orc(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Orc, self).__init__(sex, subrace, level)


class Tabaxi(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Tabaxi, self).__init__(sex, subrace, level)


class Tiefling(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Tiefling, self).__init__(sex, subrace, level)


class Triton(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Triton, self).__init__(sex, subrace, level)


class Yuanti(_RaceBuilder):
    def __init__(self, sex, subrace, level) -> None:
        super(Yuanti, self).__init__(sex, subrace, level)


def get_subraces_by_race(race: str):
    """Yields a list of valid subraces by race.

    :param str race: Race to retrieve subraces for.

    """
    for subrace in PC_SUBRACES:
        if Load.get_columns(subrace, "parent", source_file="subraces") == race:
            yield subrace


def has_subraces(race: str) -> bool:
    """
    Determines if race has subraces.

    :param str race: Race to determine if it has subraces.

    """
    try:
        return [s for s in get_subraces_by_race(race)][0]
    except IndexError:
        return False
