import { ActionOptions } from "gadget-server";

export const run: ActionRun = async ({ api }): Promise<string[]> => {
  const roles = await api.JobRoles.findMany({
    filter: { deletedAt: { isSet: false } },
    sort: { roleName: "Ascending" },
    select: {
      roleName: true
    }
  });

  return roles
    .map(role => role.roleName)
    .filter((name): name is string => name != null);
};

export const options: ActionOptions = {
  returnType: true,
  triggers: { api: true }
};
