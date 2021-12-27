from docs.sample.decorators.summary import app

def test_tags_in_spec():
    spec = app.api_spec.to_dict()
    assert "summary" in spec["paths"]["/summary"]["get"]
    summary = spec["paths"]["/summary"]["get"]["summary"]
    assert "This is a short description of the operation" == summary
