from SDG_KEYWORDS.sdg_keywords_merger import SDGKeywordsMerger

class KEYWORDS_MERGER_SECTION():
    def merge_sdg_keywords(self):
        """
            Merges SDG-specific keywords that were compiled from a number of different sources.
        """
        SDGKeywordsMerger().merge()