import Operations from './operations.js'
const {createApp} = Vue;
const app = createApp({
    components: {
        Operations,
    }
});
app.mount('#app');