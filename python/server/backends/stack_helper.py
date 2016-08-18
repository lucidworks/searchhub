from schedule_helper import create_schedule


def create_stack_datasource_configs(project):
    pipeline = project["stack_pipeline"]
    if pipeline is None:
        pipeline = "stack-overflow-default"
    configs = []
    schedules = []
    # TODO: should we have one crawler for all the websites under this project or one crawler per website?
    if "stacks" in project:
        config, schedule = create_config(project["name"], project["label"], project["includes"], project["excludes"], project["schedule"], pipeline, project["stacks"])
        configs.append(config)
        schedules.append(schedule)

    return configs, schedules


def create_config(project_name, project_label, includes, excludes, schedule, pipeline, stacks):
    stack_links = []
    for stack in stacks:
        stack_links.append("http://stackoverflow.com/questions/tagged/" + stack["tag"])
    config = {
        'id': "stack-{0}".format(project_name),
        "connector": "lucid.anda",
        "type": "web",
        'pipeline': pipeline,
        "properties": {
            "refreshOlderThan": -1,
            "f.appendTrailingSlashToLinks": False,
            "refreshErrors": False,
            "restrictToTreeIgnoredHostPrefixes": [
                "www."
            ],
            "f.excludeSelectors": [
                "div.related",
                ".topbar",
                ".bottom-notice",
                "#hot-network-questions",
                "#footer"
            ],
            "f.selectorFields": [
                ".post-taglist a.post-tag", ".accepted-answer .answercell",
                ".answercell",
                ".postcell .post-text"],
            "f.includeSelectors": [
                "#mainbar"
            ],
            "dedupeSaveSignature": False,
            "crawlDBType": "in-memory",
            "f.discardLinkURLQueries": False,
            "f.respectMetaEquivRedirects": False,
            "fetchDelayMS": 1000,
            "splitArchives": True,
            "refreshAll": True,
            "f.defaultMIMEType": "application/octet-stream",
            "restrictToTreeAllowSubdomains": False,
            "maxItems": -1,
            "f.scrapeLinksBeforeFiltering": False,
            "dedupe": False,
            "f.allowAllCertificates": False,
            "collection": "lucidfind",  # TODO: don't hardcode
            "forceRefresh": False,
            "f.obeyRobots": True,
            "fetchDelayMSPerHost": True,
            "indexCrawlDBToSolr": False,
            "fetchThreads": 1,
            "restrictToTree": False,
            "retainOutlinks": True,
            "f.defaultCharSet": "UTF-8",
            "emitThreads": 1,
            "excludeExtensions": [
                ".class",
                ".bin",
                ".jar"
            ],
            "diagnosticMode": False,
            "delete": True,
            "f.userAgentWebAddr": "",
            "initial_mapping": {
                "id": "FromMap",
                "mappings": [
                    {"source": "project", "target": project_name, "operation": "set"},
                    {"source": "project_label", "target": project_label, "operation": "set"},
                    {"source": "datasource_label", "target": project_label, "operation": "set"}, # we only have one crawler for SO
                    {"source": "fetchedDate", "target": "publishedOnDate", "operation": "copy"},
                    {"source": "isBot", "target": "false", "operation": "set"},
                    {
                        "source": "charSet",
                        "target": "charSet_s",
                        "operation": "move"
                    },
                    {
                        "source": "fetchedDate",
                        "target": "fetchedDate_dt",
                        "operation": "move"
                    },
                    {
                        "source": "lastModified",
                        "target": "lastModified_dt",
                        "operation": "move"
                    },
                    {
                        "source": "signature",
                        "target": "dedupeSignature_s",
                        "operation": "move"
                    },
                    {
                        "source": "contentSignature",
                        "target": "signature_s",
                        "operation": "move"
                    },
                    {
                        "source": "length",
                        "target": "length_l",
                        "operation": "move"
                    },
                    {
                        "source": "mimeType",
                        "target": "mimeType_s",
                        "operation": "move"
                    },
                    {
                        "source": "parent",
                        "target": "parent_s",
                        "operation": "move"
                    },
                    {
                        "source": "owner",
                        "target": "owner_s",
                        "operation": "move"
                    },
                    {
                        "source": "group",
                        "target": "group_s",
                        "operation": "move"
                    }
                ],
                "reservedFieldsMappingAllowed": False,
                "skip": False,
                "label": "field-mapping",
                "type": "field-mapping"
            },
            "restrictToTreeUseHostAndPath": True,
            "f.filteringRootTags": [
                "body",
                "head"
            ],
            "f.userAgentEmail": "",
            "f.timeoutMS": 10000,
            "failFastOnStartLinkFailure": True,
            "startLinks": stack_links,
            "chunkSize": 100,
            "includeRegexes": [],
            "f.obeyRobotsDelay": True,
            "deleteErrorsAfter": -1,
            "f.userAgentName": "Lucidworks-Anda/2.0",
            "retryEmit": True,
            "depth": -1,
            "refreshStartLinks": False,
            "f.maxSizeBytes": 4194304,
            "aliasExpiration": 1
        }
    }
    if excludes:
        config['properties']['excludeRegexes'] = excludes
    if includes:
        config['properties']['includeRegexes'] = includes
    if schedule:
        details = schedule
        schedule = create_schedule(details, config["id"])
    return config, schedule
