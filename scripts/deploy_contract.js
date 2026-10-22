/**
 * Hardhat deployment script for PaymentVerification smart contract.
 * For local academic testing on Hardhat Network or Ganache.
 */

const hre = require("hardhat");
const fs = require("fs");
const path = require("path");

async function main() {
    console.log("-----------------------------------------------------");
    console.log("Deploying PaymentVerification contract to local EVM...");
    console.log("-----------------------------------------------------");

    const PaymentVerification = await hre.ethers.getContractFactory("PaymentVerification");
    const contract = await PaymentVerification.deploy();

    await contract.waitForDeployment();
    const contractAddress = await contract.getAddress();

    console.log(`✅ PaymentVerification successfully deployed to: ${contractAddress}`);

    // Export contract deployment artifact for Python Web3.py consumption
    const deploymentInfo = {
        network: hre.network.name,
        address: contractAddress,
        deployedAt: new Date().toISOString()
    };

    const outPath = path.join(__dirname, "../contracts/deployment_info.json");
    fs.writeFileSync(outPath, JSON.stringify(deploymentInfo, null, 2));
    console.log(`Saved deployment info to: ${outPath}`);
}

main().catch((error) => {
    console.error("Deployment failed:", error);
    process.exitCode = 1;
});
