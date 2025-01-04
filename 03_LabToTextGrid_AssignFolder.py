import os
import re

class ExtentionException(Exception):
    pass

class EmptyLabelException(Exception):
    pass

class Segment:
    def __init__(self, tStart, tEnd, label):
        self.tStart = tStart
        self.tEnd = tEnd
        self.label = label

    def __add__(self, other):
        return Segment(self.tStart, other.tEnd, self.label + other.label)

    def can_follow(self, other):
        vowels = ['a', 'i', 'u', 'e', 'o', 'a:', 'i:', 'u:', 'e:', 'o:']
        consonants = ['w', 'r', 't', 'y', 'p', 's', 'd', 'f', 'g', 'h', 'j',
                      'k', 'z', 'c', 'b', 'n', 'm']
        only_consonants = lambda x: all([c in consonants for c in x])
        if only_consonants(other.label) and self.label in vowels:
            return True
        if only_consonants(other.label) and only_consonants(self.label):
            return True
        return False

    def to_textgrid_lines(self, segmentIndex):
        label = '' if self.label in ['silB', 'silE'] else self.label
        return [f'        intervals [{segmentIndex}]:',
                f'            xmin = {self.tStart} ',
                f'            xmax = {self.tEnd} ',
                f'            text = "{label}" ']


class SegmentationLabel:
    def __init__(self, segments, separatedByMora=False):
        self.segments = segments
        self.separatedByMora = separatedByMora

    def by_moras(self):
        if self.separatedByMora:
            return self

        moraSegments = []
        curMoraSegment = None
        for segment in self.segments:
            if curMoraSegment is None:
                curMoraSegment = segment
            elif segment.can_follow(curMoraSegment):
                curMoraSegment += segment
            else:
                moraSegments.append(curMoraSegment)
                curMoraSegment = segment
        if curMoraSegment:
            moraSegments.append(curMoraSegment)
        return SegmentationLabel(moraSegments, separatedByMora=True)

    def to_textgrid(self, textgridFileName):
        if not self.segments:
            raise EmptyLabelException(f'No label data found in {textgridFileName}')
        textgridLines = self._textgrid_headers()
        for i, segment in enumerate(self.segments):
            textgridLines.extend(segment.to_textgrid_lines(i + 1))
        with open(textgridFileName, 'w') as f:
            f.write('\n'.join(textgridLines))

    def _textgrid_headers(self):
        segmentKind = 'mora' if self.separatedByMora else 'phoneme'
        return ['File type = "ooTextFile"',
                'Object class = "TextGrid"',
                ' ',
                'xmin = 0 ',
               f'xmax = {self.segments[-1].tEnd} ',
                'tiers? <exists> ',
                'size = 1 ',
                'item []: ',
                '    item [1]: ',
                '        class = "IntervalTier" ',
               f'        name = "{segmentKind}" ',
                '        xmin = 0 ',
               f'        xmax = {self.segments[-1].tEnd} ',
               f'        intervals: size = {len(self.segments)} ']


def read_lab(filename):
    if not re.search(r'\.lab$', filename):
        raise ExtentionException(f"{filename} is not a .lab file")
    with open(filename, 'r') as f:
        labeldata = [line.split() for line in f if line.strip()]
        segments = [Segment(float(line[0]), float(line[1]), line[2])
                    for line in labeldata]
        return SegmentationLabel(segments)


def process_lab_files(input_folder, output_folder, by_moras=False):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    lab_files = [f for f in os.listdir(input_folder) if f.endswith('.lab')]

    for lab_file in lab_files:
        lab_path = os.path.join(input_folder, lab_file)
        try:
            label = read_lab(lab_path)
            if by_moras:
                label = label.by_moras()
            textgrid_file = os.path.join(output_folder, lab_file.replace('.lab', '.TextGrid'))
            label.to_textgrid(textgrid_file)
            print(f"Processed: {lab_file} -> {textgrid_file}")
        except (ExtentionException, EmptyLabelException) as e:
            print(f"Skipping {lab_file}: {e}")


if __name__ == '__main__':
    input_folder = input("Enter input folder path: ").strip()
    output_folder = input("Enter output folder path: ").strip()
    by_moras = input("Segment by moras? (y/n): ").strip().lower() == 'y'

    process_lab_files(input_folder, output_folder, by_moras)
