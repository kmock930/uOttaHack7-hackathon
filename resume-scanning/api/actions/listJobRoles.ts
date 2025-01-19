import { ActionOptions } from "gadget-server";

/** Type definition for select input options */

/**
 * Lists all active job roles in the system, returning them in a format suitable for select inputs.
 * Only returns non-deleted roles, ordered alphabetically by name.
 * @param {Object} context - The action context
 * @param {Logger} context.logger - Logger instance
 * @param {ApiClient} context.api - API client instance
 * @returns {Promise<SelectOption[]>} Array of select options with role names
 */
export const run: ActionRun = async ({ api, logger }): Promise<String[]> => {
  try {
    const roles = await api.JobRoles.findMany({
      filter: { deletedAt: { isSet: false } },
      sort: { roleName: "Ascending" },
      select: { roleName: true }
    });

    logger.info({ roleCount: roles.length }, "Found job roles");

    return roles.map((role) => role?.roleName).filter((roleName): roleName is string => roleName !== null);
  } catch (error) {
    logger.error({ error }, "Failed to fetch job roles");
    throw new Error("Failed to fetch job roles");
  }
};

export const options: ActionOptions = {
  returnType: true,
  triggers: { api: true },
  timeoutMS: 10000
};
