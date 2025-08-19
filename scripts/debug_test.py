import sys
sys.path.append('src')
from address_parser import AddressParser

parser = AddressParser()

test = 'istanbul mecidiyekoy'
words = test.split()
print(f'Original words: {words}')

components = {'il': 'İstanbul'}
province_name = components.get('il', '').lower()
print(f'Province name (lowercase): {province_name}')

filtered_words = []
for word in words:
    print(f'  Word: {word} -> {word.lower()}')
    if word.lower() != province_name:
        filtered_words.append(word)
        print(f'    INCLUDED')
    else:
        print(f'    EXCLUDED')

print(f'Filtered words: {filtered_words}')