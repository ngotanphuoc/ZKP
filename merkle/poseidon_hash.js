const { buildPoseidon } = require("circomlibjs");

(async () => {
    const poseidon = await buildPoseidon();
    const F = poseidon.F;
    const a = BigInt(process.argv[2]);
    const b = BigInt(process.argv[3]);
    const hash = poseidon([a, b]);
    console.log(F.toString(hash));
})();