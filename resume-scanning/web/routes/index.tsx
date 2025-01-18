import { Box, Panel, Text, Flex, Link } from "@bigcommerce/big-design";
import { CheckIcon, StoreIcon } from '@bigcommerce/big-design-icons';
import { useFindFirst } from "@gadgetinc/react";
import { api } from "../api";

export default function() {
  // @ts-ignore
  const [{ data, fetching, error }] = useFindFirst(api.bigcommerce.store);

  return (
    <>
      <Panel description={<Flex flexGap={"8px"}><CheckIcon color="success" /> <Text>Successfully connected your Gadget app to BigCommerce</Text></Flex>}>
        <div style={{ width: "100%" }}>
          <Flex flexDirection="column" alignItems="center">
            <img
              src="https://assets.gadget.dev/assets/icon.svg"
              style={{
                margin: "14px auto",
                height: "44px",
              }}
            />
            <Text>Edit this page: <Link target="_blank" href={`/edit/${process.env.GADGET_PUBLIC_APP_ENV}/files/web/routes/index.tsx`}>web/routes/index.tsx</Link></Text>
          </Flex>
        </div>
      </Panel>
      <Panel description={<Text>Store record fetched from: <Link target="_blank" href={`/edit/${process.env.GADGET_PUBLIC_APP_ENV}/model/DataModel-BigCommerce-Store/data`}>api/models/bigcommerce/store/data</Link></Text>}>
        <Box border="box" padding="xSmall">
          <Flex flexGap={"16px"}><StoreIcon color="secondary60" />
            <Text color="secondary60">
              {
                // @ts-ignore
                `store-${data?.storeHash}.mybigcommerce.com`
              }
            </Text>
          </Flex>
        </Box>
      </Panel>
    </>
  );
}
