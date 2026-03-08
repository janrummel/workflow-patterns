"""Tests for feed presets and selection logic."""

from content_workflow.presets import CATEGORIES, FeedSource, parse_selection, estimate_cost


class TestPresetData:
    """Verify preset data integrity."""

    def test_has_six_categories(self):
        assert len(CATEGORIES) == 6

    def test_each_category_has_ten_feeds(self):
        for name, feeds in CATEGORIES.items():
            assert len(feeds) == 10, f"{name} has {len(feeds)} feeds, expected 10"

    def test_all_feeds_have_required_fields(self):
        for name, feeds in CATEGORIES.items():
            for feed in feeds:
                assert isinstance(feed, FeedSource)
                assert feed.name, f"Feed in {name} missing name"
                assert feed.url.startswith("http"), f"{feed.name} URL invalid: {feed.url}"
                assert feed.description, f"{feed.name} missing description"

    def test_no_duplicate_urls_within_category(self):
        for name, feeds in CATEGORIES.items():
            urls = [f.url for f in feeds]
            assert len(urls) == len(set(urls)), f"Duplicate URLs in {name}"


class TestParseSelection:
    """Test user input parsing."""

    def test_single_number(self):
        assert parse_selection("3", max_items=10) == [2]

    def test_comma_separated(self):
        assert parse_selection("1,3,5", max_items=10) == [0, 2, 4]

    def test_all_keyword(self):
        assert parse_selection("all", max_items=3) == [0, 1, 2]

    def test_range(self):
        assert parse_selection("2-5", max_items=10) == [1, 2, 3, 4]

    def test_mixed_range_and_numbers(self):
        assert parse_selection("1,3-5,8", max_items=10) == [0, 2, 3, 4, 7]

    def test_out_of_range_ignored(self):
        assert parse_selection("1,99", max_items=5) == [0]

    def test_whitespace_tolerance(self):
        assert parse_selection(" 1 , 3 , 5 ", max_items=10) == [0, 2, 4]

    def test_empty_returns_empty(self):
        assert parse_selection("", max_items=10) == []

    def test_deduplication(self):
        assert parse_selection("1,1,2", max_items=10) == [0, 1]


class TestEstimateCost:
    """Test cost estimation display."""

    def test_basic_estimate(self):
        result = estimate_cost(num_articles=9)
        assert "9" in result
        assert "$" in result

    def test_zero_articles(self):
        result = estimate_cost(num_articles=0)
        assert "0" in result
