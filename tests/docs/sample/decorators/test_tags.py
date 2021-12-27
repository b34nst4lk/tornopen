from docs.sample.decorators.tags import app

def test_tags_in_spec():
    spec = app.api_spec.to_dict()
    assert "tags" in spec["paths"]["/tagged"]["get"]
    tags = spec["paths"]["/tagged"]["get"]["tags"]
    assert "tag_1" in tags
    assert "tag_2" in tags
