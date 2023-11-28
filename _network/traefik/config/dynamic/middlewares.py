output_config = {
    "input": {
        "type": "http",
        "middleware": {
            "rewrite-redirect-https": {
                "name": "rewrite-response-headers",
                "plugin": True,
                "rewrites": [
                    {
                        "header": "Location",
                        "regex": "^http://(.+)$",
                        "replacement": "https://$1",
                    }
                ],
            }
        },
    }
}
