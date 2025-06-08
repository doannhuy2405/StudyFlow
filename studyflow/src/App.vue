
<script setup>
 import { RouterView, useRouter } from 'vue-router';
  import { provide, ref } from "vue";


  const isLoggedIn = ref(false);
  const router = useRouter();

  const login = () => {
    isLoggedIn.value=true;
    router.push("/home"); //Chuyển hướng sau khi đăng nhập thành công
  }

  //Cung cấp cho component con
  provide("isLoggedIn", isLoggedIn);
  provide("login", login);


  //Ngôn ngữ
  const language = ref("vi"); // Ngôn ngữ mặc định là tiếng Việt

  const currentPage = ref ('landingpage');
  provide('currentPage', currentPage); //cung cấp currentPage để các component có thể thay đổi

  const toggleLanguage = () => {
    language.value = language.value === "vi" ? "en" : "vi";
    console.log(language.value)
  };


</script>

<template>
  <RouterView :language="language" :toggleLanguage="toggleLanguage" />
</template>

<style scoped>
</style>
