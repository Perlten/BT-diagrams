import astroid
from astroid.exceptions import AstroidImportError

from src.core.policies.FilePolicies import (
    BTFilePolicy,
    FilePolicyCantDependPolicy,
    FilePolicyMustDependPolicy,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.bt_module import BTModule


class BTFile:
    label: str = ""
    policies: list[BTFilePolicy] = None
    edge_to: list["BTFile"] = None
    ast = None
    module: "BTModule" = None

    def __init__(self, label: str, module, code_path: str = None):
        print(f"create {label}")
        self.label = label
        self.ast = None

        if code_path is not None:
            self.ast: astroid.Module = astroid.MANAGER.ast_from_module_name(code_path)

        self.edge_to = []
        self.policies = []
        self.module = module

    @property
    def file(self):
        if self.ast:
            return self.ast.file
        return ""

    @property
    def uid(self):
        if self.ast:
            return self.ast.file
        else:
            return self.label

    @property
    def module_path(self) -> str | None:
        if not self.ast:
            return None
        return "/".join(self.file.split("/")[:-1])

    def validate(self) -> bool:
        for policy in self.policies:
            if not policy.validate(self.edge_to):
                return False
        return True

    def __rshift__(self, other):
        if isinstance(other, list):
            existing_edges = set(
                [edge.file for edge in self.edge_to if edge.file != ""]
            )
            new_node_list = filter(lambda e: e.file not in existing_edges, other)
            self.edge_to.extend([node for node in new_node_list])
        else:
            edges = set([edge.file for edge in self.edge_to])
            if other.file in edges:
                return

            self.edge_to.append(other)

    def cant_depend_on(self, other):
        policy = FilePolicyCantDependPolicy(other)
        self.policies.append(policy)

    def must_depend_on(self, other):
        policy = FilePolicyMustDependPolicy(other)
        self.policies.append(policy)


def get_imported_modules(ast: astroid.Module, root_location: str):
    imported_modules = []
    for sub_node in ast.body:
        try:
            if isinstance(sub_node, astroid.node_classes.ImportFrom):
                sub_node: astroid.node_classes.ImportFrom = sub_node

                try:
                    module_node = astroid.MANAGER.ast_from_module_name(
                        sub_node.modname + "." + sub_node.names[0][0],
                        context_file=root_location,
                    )
                except Exception:
                    module_node = astroid.MANAGER.ast_from_module_name(
                        sub_node.modname,
                        context_file=root_location,
                    )
                imported_modules.append(module_node)

            if isinstance(sub_node, astroid.node_classes.Import):
                pass  # TODO!!

        except AstroidImportError as e:
            continue

    return imported_modules
