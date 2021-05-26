from typing import List
from binary_reader import *

class Test(BrStruct):
    def __br_read__(self, br: 'BinaryReader'):
        self.count = br.read_int16()
        self.nums = br.read_int32(self.count)
        self.f = br.read_float()
        self.s = []

        for _ in range(self.count):
            self.s.append(br.read_str())

    count: uint16
    nums: List[int32]
    f: float
    s: List[str]

    @count_of('nums', 's')
    def countOfSomeList(self):
        return self.count

    @length_of('s')
    def lengthOfString(self):
        return 0

class Offset(BrStruct):
    offset: int32
    value: str

    @offset_of('value')
    def stringOffset(self):
        return self.offset

    @is_offset(('offset', 'value'))
    def stringWriteOffset(self, val):
        return val

    @null('value')
    def nullStr(self):
        return True


def main():
    with BinaryReader(bytearray(b'\x00\x00\x00\x10\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x3F\x80\x00\x00String'), Endian.BIG) as br:
        o: Offset = br.read_struct(Offset, check_attrs=True)
        print(o.offset)
        print(o.value)
        
        br.seek(0)
        br.write_struct(o)
        print(br.buffer())
        
        br.seek(0)
        o: Offset = br.read_struct(Offset, check_attrs=True)
        print(o.offset)
        print(o.value)
        

    # with BinaryReader(bytearray(b'\x00\x03\x00\x00\x00\x04\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF\x3F\x80\x00\x00Test\x00Null\x00String\x00'), Endian.BIG) as br:
    #     x: Test = br.read_struct(Test, False)
    #     print(x.count)
    #     print(x.nums)
    #     print(x.f)
    #     print(x.s)

    #     br.seek(0)
    #     br.write_int16(2)
    #     br.write_int32(-1)
    #     br.write_int32(5)
    #     br.write_float(0.5)
    #     br.write_str('Testing', True)
    #     br.write_str('Testing more', True)
    #     br.seek(0)

    #     x = br.read_struct(Test, False)
    #     print(x.count)
    #     print(x.nums)
    #     print(x.f)
    #     print(x.s)

        


if __name__ == '__main__':
    main()
