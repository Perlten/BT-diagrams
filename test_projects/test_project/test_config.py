from src.core.bt_graph import BTGraph
import tp_src as test_project


def update(graph: BTGraph):
    api_file = graph.get_bt_file("api.api")
    core_file = graph.get_bt_file("tp_core.core")
    api_file.must_depend_on(core_file)

    api_module = graph.get_bt_module("api")
    sub_api_module = graph.get_bt_module("api.sub_api")
    controller_module = graph.get_bt_module("controller")
    core_module = graph.get_bt_module("tp_core")

    api_module.cant_depend_on(controller_module)
    sub_api_module.cant_depend_on(core_module)


def settings():
    return {
        "diagram_name": "test project",
        "project": test_project,
    }
