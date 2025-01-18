import type { GadgetModel } from "gadget-server";

// This file describes the schema for the "JobRoles" model, go to https://resume-scanning.gadget.app/edit to view/edit your model in Gadget
// For more information on how to update this file http://docs.gadget.dev

export const schema: GadgetModel = {
  type: "gadget/model-schema/v1",
  storageKey: "LPFnYB1egbVJ",
  fields: {
    createdBy: { type: "string", storageKey: "60WcLJfiqvwQ" },
    deletedAt: {
      type: "dateTime",
      includeTime: true,
      storageKey: "50gFkku67X57",
    },
    deletedBy: { type: "string", storageKey: "swjPtb180xp3" },
    roleName: { type: "string", storageKey: "CB0mcJSGSUdp" },
    updatedBy: { type: "string", storageKey: "uZ4EYTCU68kO" },
  },
};
