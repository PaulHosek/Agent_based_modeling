# eu_countries = ["Austria", "Belgium", "Bulgaria", "Croatia", "Cyprus", "Czech Republic",  # Paul
#                 "Denmark", "Estonia", "Finland", "France", "Germany", "Greece", # Tijn
#                 "Hungary", "Ireland", "Italy", "Latvia", "Lithuania", # Gaia
#                 "Luxembourg", "Malta", "Netherlands", "Poland", "Portugal",
#                 "Romania", "Slovakia", "Slovenia", "Spain", "Sweden"]

austria = [("Austria", "Germany"),
           ("Austria", "Czech Republic"),
           ("Austria", "Slovakia"),
            ('Austria', 'Slovenia'),
           ("Austria", "Hungary"),
           ("Austria", "Italy")]

belgium = [("Belgium", "Netherlands"),
           ("Belgium", "Germany"),
           ("Belgium", "Luxembourg"),
           ("Belgium", "France")]

bulgaria = [("Bulgaria", "Greece"),
            ("Bulgaria", "Romania")]

croatia = [("Croatia", "Slovenia"),
           ("Croatia", "Hungary")]

cyprus = []

czechia = [("Czech Republic", "Germany"),
           ("Czech Republic", "Poland"),
           ("Czech Republic", "Slovakia")]

denmark = [("Denmark", "Germany"),
           ("Denmark", "Sweden")]

estonia = [("Estonia", "Latvia")]

finland = [("Finland", "Sweden")]

france = [("France", "Spain"),
          ("France", "Belgium"),
          ("France", "Italy"),
          ("France", "Germany"),
          ("France", "Luxembourg")]

germany = [("Germany", "Netherlands"),
           ("Germany", "Belgium"),
           ("Germany", "Denmark"),
           ("Germany", "Czech Republic"),
           ("Germany", "Luxembourg"),
           ("Germany", "France"),
           ("Germany", "Austria"),
           ("Germany", "Poland")]

greece = [("Greece", "Bulgaria")]

hungary = [("Hungary", "Austria"),
           ("Hungary", "Croatia"),
           ("Hungary", "Romania"),
           ("Hungary", "Slovakia"),
           ("Hungary", "Slovenia")]

ireland = []

italy = [("Italy", "Slovenia"),
         ("Italy", "Austria"),
         ("Italy", "France")]

latvia = [("Latvia", "Lithuania"),
          ("Latvia", "Estonia")]

lithuania = [("Lithuania", "Latvia"),
             ("Lithuania", "Poland")]

luxembourg = [("Luxembourg", "Belgium"),
              ("Luxembourg", "Germany"),
              ("Luxembourg", "France")]
malta = []

netherlands = [("Netherlands", "Germany"),
               ("Netherlands", "Belgium")]

poland = [("Poland", "Germany"),
          ("Poland", "Slovakia"),
          ("Poland", "Czech Republic"),
          ("Poland", "Lithuania")]

portugal = [("Portugal", "Spain")]

romania = [("Romania", "Hungary"),
           ("Romania", "Bulgaria")]

slovakia = [("Slovakia", "Czech Republic"),
            ("Slovakia", "Austria"),
            ("Slovakia", "Poland"),
            ("Slovakia", "Hungary")]

slovenia = [("Slovenia", "Italy"),
            ("Slovenia", "Austria"),
            ("Slovenia", "Croatia"),
            ("Slovenia", "Hungary")]

spain = [("Spain", "Portugal"),
         ("Spain", "France")]

sweden = [("Sweden", "Finland"),
          ("Sweden", "Denmark")]

#####
globals_list = [i for i in list(globals().values()) if isinstance(i, list)]
flat_list = [item for sublist in globals_list for item in sublist]

print(flat_list)

print(len(flat_list))
countries = flat_list

unique_countries = []
for country in countries:
    country = tuple(sorted(country))
    if country not in unique_countries:
        unique_countries.append(country)
print(len(unique_countries))
print('unique', unique_countries)
# o_eu_borders = [
#         ("Austria", "Germany"),
#         ("Austria", "Czech Republic"),
#         ("Austria", "Slovakia"),
#         ("Austria", "Slovenia"),
#         ("Austria", "Italy"),
#         ("Belgium", "Netherlands"),
#         ("Belgium", "Germany"),
#         ("Belgium", "Luxembourg"),
#         ("Belgium", "France"),
#         ("Bulgaria", "Romania"),
#         ("Bulgaria", "Greece"),
#         ("Croatia", "Slovenia"),
#         ("Croatia", "Hungary"),
#         ("Czech Republic", "Germany"),
#         ("Czech Republic", "Poland"),
#         ("Czech Republic", "Slovakia"),
#         ("Denmark", "Germany"),
#         ("Estonia", "Latvia"),
#         ("Finland", "Sweden"),
#         ("France", "Belgium"),
#         ("France", "Luxembourg"),
#         ("France", "Germany"),
#         ("France", "Italy"),
#         ("Germany", "Denmark"),
#         ("Germany", "Poland"),
#         ("Germany", "Czech Republic"),
#         ("Germany", "Austria"),
#         ("Germany", "Netherlands"),
#         ("Greece", "Bulgaria"),
#         ("Hungary", "Austria"),
#         ("Hungary", "Slovakia"),
#         ("Hungary", "Romania"),
#         ("Italy", "Austria"),
#         ("Italy", "Slovenia"),
#         ("Latvia", "Lithuania"),
#         ("Lithuania", "Poland"),
#         ("Luxembourg", "Belgium"),
#         ("Luxembourg", "Germany"),
#         ("Malta", "Italy"),
#         ("Netherlands", "Belgium"),
#         ("Netherlands", "Germany"),
#         ("Poland", "Germany"),
#         ("Poland", "Czech Republic"),
#         ("Poland", "Slovakia")]
# flat_o = [item for sublist in o_eu_borders for item in sublist]
#
#
#
#
# print("new")
# # print([elem for elem in unique_countries if elem not in o_eu_borders])
# print([elem for elem in o_eu_borders if elem not in flat_list])
