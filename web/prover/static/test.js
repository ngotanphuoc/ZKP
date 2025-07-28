// const circomlibjs = require('circomlibjs');

// function strToBigInt(str) {
//   let hex = '';
//   for (let i = 0; i < str.length; i++) {
//     hex += str.charCodeAt(i).toString(16).padStart(2, '0');
//   }
//   return BigInt('0x' + hex);
// }

// async function hashLeaf(email, secret) {
//   const poseidon = await circomlibjs.buildPoseidon();
//   const emailBigInt = strToBigInt(email);
//   const secretBigInt = strToBigInt(secret);
//   const hash = poseidon.F.toString(poseidon([emailBigInt, secretBigInt]));
//   return poseidon.F.toString(poseidon([emailBigInt, secretBigInt]));
// }

// // Ví dụ sử dụng
// (async () => {
//   const hash = await hashLeaf('alice@it.company.com', 'mysecret');
//   console.log('Poseidon hash:', hash);
// })();
(async () => {
    try {
      const poseidon = await ZKLibs.buildPoseidon();
      const hash = poseidon(["1", "2"]);
      console.log("Poseidon hash:", poseidon.F.toString(hash));
    } catch (err) {
      console.error("Lỗi khi gọi ffjavascript / poseidon:", err);
    }
  })();