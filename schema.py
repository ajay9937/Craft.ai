session_schema = {
    "type": "array",
    "minItems": 7,
    "maxItems": 7,
    "prefixItems": [

        # 1. File paths -> purpose
        {
            "type": "object",
            "description": "A mapping where each key is a relative project file path and each value describes the usage and purpose of that file.",
            "additionalProperties": {
                "type": "string"
            }
        },

        # 2. Basic app features
        {
            "type": "array",
            "description": "A list of basic professional features appropriate for a modern 2026 mobile application. Features must not require an external server or AI model.",
            "items": {
                "type": "string"
            }
        },

        # 3. JS/Python backend description
        {
            "type": "object",
            "description": "A complete description of the JavaScript and Python backend/intercommunication architecture, including modules, functions, parameters, and function signatures.",
            "properties": {
                "description": {
                    "type": "string"
                },
                "javascript": {
                    "type": "object",
                    "properties": {
                        "modules": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "functions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string"
                                    },
                                    "parameters": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "signature": {
                                        "type": "string"
                                    },
                                    "description": {
                                        "type": "string"
                                    }
                                },
                                "required": [
                                    "name",
                                    "parameters",
                                    "signature",
                                    "description"
                                ]
                            }
                        }
                    },
                    "required": [
                        "modules",
                        "functions"
                    ]
                },
                "python": {
                    "type": "object",
                    "properties": {
                        "modules": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            }
                        },
                        "functions": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string"
                                    },
                                    "parameters": {
                                        "type": "array",
                                        "items": {
                                            "type": "string"
                                        }
                                    },
                                    "signature": {
                                        "type": "string"
                                    },
                                    "description": {
                                        "type": "string"
                                    }
                                },
                                "required": [
                                    "name",
                                    "parameters",
                                    "signature",
                                    "description"
                                ]
                            }
                        }
                    },
                    "required": [
                        "modules",
                        "functions"
                    ]
                },
                "communication": {
                    "type": "string",
                    "description": "How JavaScript and Python communicate with each other."
                }
            },
            "required": [
                "description",
                "javascript",
                "python",
                "communication"
            ]
        },

        # 4. Debugging calls
        {
            "type": "array",
            "description": "JavaScript function calls that invoke Python functions for debugging.",
            "items": {
                "type": "string"
            }
        },

        # 5. Non-technical app description
        {
            "type": "string",
            "description": "A short non-technical description explaining what kind of app is being planned and what features it provides. It must be understandable to a non-programmer."
        },

        {
            "type": "array",
            "description": "Python libraries used by the application",
            "items": {
                "type": "string"
            }
        },

        {
            "type": "object",
            "description": "URL of files needed to be download and saved beforehand.",
            "additionalProperties": {
                "type": "string"
            }
        },
    ]
}

update_schema = {
  "type": "array",
  "minItems": 2,
  "maxItems": 2,
  "prefixItems": [
    {
      "type": "array",
      "description": "The first element: An array of edit instructions.",
      "items": {
        "type": "array",
        "minItems": 3,
        "maxItems": 3,
        "prefixItems": [
          {
            "type": "integer",
            "description": "start_line_index (inclusive)"
          },
          {
            "type": "integer",
            "description": "end_line_index (exclusive)"
          },
          {
            "type": "string",
            "description": "replacement_text"
          }
        ]
      }
    },
    {
      "type": "object",
      "description": "The second element: A dictionary of downloadable files.",
      "additionalProperties": {
        "type": "string",
        "format": "uri",
        "description": "The downloadable URL"
      }
    }
  ]
}

generative_schema = {
    "type": "array",
    "minItems": 2,
    "maxItems": 2,
    "prefixItems": [
        {
            "type": "array",
            "description": "An array of all online URLs used in the code (CDNs, images, .js, .css). This MUST come before the code.",
            "items": {
                "type": "string",
                "format": "uri"
            }
        },
        {
            "type": "string",
            "description": "The complete, raw, plain-text production code for the file. No markdown formatting."
        }
    ]
}