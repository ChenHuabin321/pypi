from chb._imports import *
class GetFirstLetter(object):
    def is_contain_chinese(self, check_str):
        """
        判断字符串中是否包含中文
        :param check_str: {str} 需要检测的字符串
        :return: {bool} 包含返回True， 不包含返回False
        """
        for ch in check_str:
            if u'\u4e00' <= ch <= u'\u9fff':
                return True
        return False

    def single_get_first(self, string):
        """
        获取全拼的首字母
        """
        p = xpinyin.Pinyin()
        py = p.get_pinyin(string)
        return py[0]

    def getPinyin(self, string):
        """
        输出所有字的首字母
        """
        if string == None:
            return None
        string = string.replace('（', '(')
        s_list = string.split('(')
        s2_list = []
        for s in s_list:
            s = re.sub("[A-Za-z0-9\!\%\[\]\,\。（）()*-+=/]", "", s)
            lst = list(s)
            charLst = []
            for l in lst:
                charLst.append(self.single_get_first(l))
            s2_list.append(''.join(charLst))
        return '_'.join(s2_list)

if __name__=='__main__':
    g = GetFirstLetter()
    print(g.getPinyin('陈华彬'))