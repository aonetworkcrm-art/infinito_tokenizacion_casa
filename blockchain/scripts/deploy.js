/**
 * 🚀 Deploy Script — InfinitoToken (TI)
 * =======================================
 * Despliega el token en Polygon Amoy Testnet
 *
 * Uso:
 *   npx hardhat run scripts/deploy.js --network amoy
 *
 * @author Romny (El Joker) + Buffy (Codebuff AI)
 */

import hre from "hardhat";
import dotenv from "dotenv";
dotenv.config();

async function main() {
  console.log("=".repeat(60));
  console.log("🚀 INFINITO TOKEN — Deployment");
  console.log("=".repeat(60));
  console.log(`\nNetwork: ${hre.network.name} (Chain ID: ${hre.network.config.chainId})`);

  const [deployer] = await hre.ethers.getSigners();
  console.log(`Deployer: ${deployer.address}`);
  console.log(`Balance:  ${hre.ethers.formatEther(await hre.ethers.provider.getBalance(deployer.address))} MATIC\n`);

  // ─── CONFIGURACIÓN ───
  const TREASURY_ADDRESS = process.env.TREASURY_ADDRESS || deployer.address;
  const PADRES_ADDRESS   = process.env.PADRES_ADDRESS   || deployer.address;
  const JOKER_ADDRESS    = process.env.JOKER_ADDRESS    || deployer.address;

  console.log("📋 Deploy Parameters:");
  console.log(`   Treasury: ${TREASURY_ADDRESS}`);
  console.log(`   Padres:   ${PADRES_ADDRESS}`);
  console.log(`   Joker:    ${JOKER_ADDRESS}`);

  // ─── DEPLOY ───
  console.log("\n⏳ Deploying InfinitoToken...");
  const InfinitoToken = await hre.ethers.getContractFactory("InfinitoToken");
  const token = await InfinitoToken.deploy(TREASURY_ADDRESS, PADRES_ADDRESS, JOKER_ADDRESS);
  await token.waitForDeployment();

  const tokenAddress = await token.getAddress();
  console.log(`\n✅ InfinitoToken deployed at: ${tokenAddress}`);

  // ─── UNPAUSE ───
  console.log("\n⏳ Unpausing contract...");
  const tx = await token.unpause();
  await tx.wait();
  console.log("✅ Contract unpaused");

  // ─── VERIFICACIÓN ───
  console.log("\n📊 Contract State:");
  const totalSupply = await token.totalSupply();
  const name = await token.name();
  const symbol = await token.symbol();
  const decimals = await token.decimals();
  const owner = await token.hasRole(await token.DEFAULT_ADMIN_ROLE(), JOKER_ADDRESS);
  const paused = await token.paused();

  console.log(`   Name:        ${name}`);
  console.log(`   Symbol:      ${symbol}`);
  console.log(`   Decimals:    ${decimals}`);
  console.log(`   Total Supply: ${hre.ethers.formatEther(totalSupply)} ${symbol}`);
  console.log(`   Joker Admin:  ${owner ? "✅" : "❌"}`);
  console.log(`   Paused:       ${paused ? "⏸️ Yes" : "✅ No"}`);

  console.log("\n📋 Beneficiary Balances:");
  const padresBal = await token.balanceOf(PADRES_ADDRESS);
  const jokerBal = await token.balanceOf(JOKER_ADDRESS);
  console.log(`   Padres (51%): ${hre.ethers.formatEther(padresBal)} TI`);
  console.log(`   Joker  (35%): ${hre.ethers.formatEther(jokerBal)} TI`);
  console.log(`   Pool   (14%): ${hre.ethers.formatEther(totalSupply - padresBal - jokerBal)} TI (in MINTER wallet)`);

  // ─── VERIFICAR EN POLYGONSCAN ───
  if (process.env.POLYGONSCAN_API_KEY) {
    console.log("\n⏳ Verifying contract on Polygonscan...");
    try {
      await hre.run("verify:verify", {
        address: tokenAddress,
        constructorArguments: [TREASURY_ADDRESS, PADRES_ADDRESS, JOKER_ADDRESS],
      });
      console.log("✅ Contract verified on Polygonscan!");
    } catch (err) {
      console.log("⚠️  Verification skipped:", err.message);
    }
  }

  console.log("\n" + "=".repeat(60));
  console.log("✅ Deploy Complete!");
  console.log(`   Explorer: https://amoy.polygonscan.com/address/${tokenAddress}`);
  console.log("=".repeat(60));
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error("\n❌ Deploy failed:", error);
    process.exitCode = 1;
  });
