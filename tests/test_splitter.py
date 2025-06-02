import unittest

from abstract_level_analyzer import split_into_sentences

class TestSplitIntoSentences(unittest.TestCase):
    def test_japanese_paragraph(self):
        text = (
            "アンパンマンが行使する暴力は男性的なものである。"
            "アンパンマンは\u300cマン\u300dという名前のとおり、男性キャラクターだ。"
            "彼は街の平和維持を担っており、その秩序を乱す存在が悪役のばいきんまんである。"
            "ばいきんまんはお手製の殺戮マシンを駆使して悪事を働くが、"
            "アンパンマンはそれに素手で対抗できる怪力の持ち主である。"
            "お決まりのパターンでは、彼の必殺技\u300cアンパンチ\u300dがばいきんまんを葬ることで物語は一件落着となる。"
            "このばいきんまんをぶっ飛ばすアンパンチは、一種の暴力である。"
            "たとえば女性のメロンパンナちゃんも\u300cメロメロパンチ\u300dという技を使うが、それを受けた者は目がハートになり錯乱するだけであるのにたいして、アンパンチはフィジカルな暴力だ。"
            "メロメロパンチとの対比において、アンパンチはジェンダー化された男性的な暴力である。"
        )
        sentences = split_into_sentences(text)
        self.assertEqual(len(sentences), 8)

    def test_single_sentence(self):
        text = "みたいなのもテストケースに含めたいわけで"
        sentences = split_into_sentences(text)
        self.assertEqual(sentences, [text])

if __name__ == "__main__":
    unittest.main()
