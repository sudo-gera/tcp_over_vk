import re
import secrets
from annotation import eat

table = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzЁАБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдежзийклмнопрстуфхцчшщъыьэюяё'
assert len(table) == 128
assert len(set(table)) == 128
untable = {w:q for q,w in enumerate(table)}

def convert(text: bytes, bin_reg1: str, bin_reg2: str) -> bytes:
    l = len(text) * 8
    text = ('{:0%ib}' % l).format(int.from_bytes(text, 'big'))[:l]
    text = re.sub(bin_reg1, bin_reg2, text)
    assert len(text) % 8 == 0
    l = len(text) // 8
    text = int('0' + text, 2).to_bytes(l, 'big')
    return text


def encode(text: eat | bytes|bytearray) -> str:
    suff = (len(text)+6)//7*7 - len(text)
    text += b'\0'*suff
    assert len(text) % 7 == 0
    text = convert(text, r'(.{7})', r'0\g<1>')
    text = ''.join([table[q] for q in text])
    assert text[len(text)-suff:] == table[0]*suff
    text = text[:len(text)-suff] + '=' * suff
    return text

def decode(text: str) -> bytes:
    suff = text.count('=')
    text = text.replace('=', table[0])
    text = bytes([untable[q] for q in text])
    text = convert(text, r'0(.{7})', r'\g<1>')
    text = text[:len(text) - suff]
    return text

if __name__ == '__main__':
    for q in range(9999):
        try:
            test = secrets.token_bytes(secrets.randbelow(256))
            etest = encode(test)
            assert test == decode(etest)
            assert all([c in table or c == '=' for c in etest])
            assert (len(test)+6)//7*8 == len(etest)
        except Exception:
            print(test)
            raise
