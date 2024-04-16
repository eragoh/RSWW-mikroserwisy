export default{
    name: 'Tours',
    props: ['description', 'page'],
    components: {},
    data() {
    return {
        tours: [],
        filter: '',
    }
},
    methods: {
        load: async function(){
            const url = '/gettoursss?page=' + this.page;
            this.tours = await (await fetch(url)).json();
        },
        
    },
    computed: {},
    mounted() {
        this.load();
    },
    template: /*html*/`
        <h3 class="text-center mt-3">{{description}}</h3>
        <div class="col-md-9">
            <div class="row">
                <div class="col-md-12 mb-3" v-for="tour in tours">
                    <div class="card">
                        <div class="row g-0">
                            <div class="col-md-4">
                                <a href="dd">
                                    <img class="card-img-top img-fluid" :src="tour.img" alt="Card image cap" style="object-fit: cover; height: 100%;">
                                </a>
                            </div>
                            <div class="col-md-8">
                                <div class="card-body">
                                    <div class="card-header">
                                        <i class="bi bi-house"></i> 
                                        <a href="ddd" style="text-decoration: none;">&nbsp{{tour.hotel}}</a>
                                    </div>
                                    <h6 class="card-title">
                                        <i class="bi bi-flag-fill"></i>
                                        {{tour.country}}, {{tour.city}}
                                    </h6>
                                    <h3 class="card-title">
                                        OPIS JAKIS ALBO COS
                                    </h3>
                                    <a href="d" class="btn btn-primary">Czytaj dalej <i class="bi bi-forward"></i></a>                   
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    




        
    `
}