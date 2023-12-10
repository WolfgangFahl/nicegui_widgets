export default {
    template: `
        <input type="text" 
               :style="style" 
               readonly 
               :size="1" 
               :value="currentIcon" 
               @click="onClick" />
    `,
    props: {
        currentIcon: String,
        style: String
    },
    methods: {
        onClick() {
            this.$emit('change');
        }
    }
};