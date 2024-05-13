export default {
    name: 'freservation',
    props: ['tourid', 'price', 'room', 'adults', 'ch3', 'ch10', 'ch18'],
    components: {},
    data() {
        return {
            tour: null,
            loading: true,
        }
    },
    methods: {
        load: async function(){
            const url = '/tours/' + this.tourid + '/get/';
            this.tour = await (await fetch(url)).json();
            this.loading = false;
        },
    },
    mounted() {
        this.load();
    },
    template: /*html*/`
        <div v-if="loading" class="loading-animation container">
            <img src="/static/loading.gif" alt="loading animation">
        </div>
        <div v-else>
            <div class="col-12" v-if="tour">
                <div class="card p-3">
                    <div class="card-body border p-0">
                        <p>
                            <a class="btn btn-primary p-2 w-100 h-100 d-flex align-items-center justify-content-between"
                                data-bs-toggle="collapse" href="#collapseExample2" role="button" aria-expanded="true"
                                aria-controls="collapseExample2">
                                <span class="fw-bold">Karta kredytowa</span>
                            </a>
                        </p>
                        <div class="collapse show p-3 pt-0" id="collapseExample2">
                            <div class="row">
                                <div class="col-lg-5 mb-lg-0 mb-3">
                                    <p class="h4 mb-0">Podsumowanie</p>
                                    <p class="mb-0"><span class="fw-bold">Produkt: </span><span class="c-green"> {{tour.hotel}}</span></p>
                                    <p class="mb-0"><span class="fw-bold">Miejsce: </span><span class="c-green"> {{ tour.country }}{{ tour.city !== '' ? ', ' + tour.city : '' }}</span></p>
                                    <p class="mb-0"><span class="fw-bold">Liczba dorosłych: </span><span class="c-green"> {{ adults }}</span></p>
                                    <p v-if="ch3 > 0" class="mb-0"><span class="fw-bold">Liczba dzieci do lat 3: </span><span class="c-green"> {{ ch3 }}</span></p>
                                    <p v-if="ch10 > 0" class="mb-0"><span class="fw-bold">Liczba dzieci do lat 10: </span><span class="c-green"> {{ ch10 }}</span></p>
                                    <p v-if="ch18 > 0" class="mb-0"><span class="fw-bold">Liczba dzieci do lat 18: </span><span class="c-green"> {{ ch18 }}</span></p>
                                    <p class="mb-0"><span class="fw-bold">Pokój: </span><span class="c-green"> {{ room }}</span></p>
                                    <p class="mb-0 text-truncate">
                                        {{tour.description}}
                                    </p>
                                </div>
                                <form class="form" method="POST">
                                <div class="row">
                                    <div class="col-12">
                                        <div class="form__div">
                                            <input hidden readonly type="text" class="form-control" placeholder=" " name="adults" :value="adults">
                                            <input hidden readonly type="text" class="form-control" placeholder=" " name="children3" :value="ch3">
                                            <input hidden readonly type="text" class="form-control" placeholder=" " name="children10" :value="ch10">
                                            <input hidden readonly type="text" class="form-control" placeholder=" " name="children18" :value="ch18">
                                            <input hidden readonly type="text" class="form-control" placeholder=" " name="room" :value="room">
                                            <input readonly type="text" class="form-control" placeholder=" " name="price" :value="price">
                                            <label for="" class="form__label">Cena</label>
                                        </div>
                                    </div>    
                                    <div class="col-12">
                                        <div class="form__div">
                                            <input required type="text" class="form-control" placeholder=" " name="card_number">
                                            <label for="" class="form__label">Numer karty</label>
                                        </div>
                                    </div>

                                    <div class="col-6">
                                        <div class="form__div">
                                            <input required type="text" class="form-control" placeholder=" " name="card_expiration_date">
                                            <label for="" class="form__label">MM / yy</label>
                                        </div>
                                    </div>

                                    <div class="col-6">
                                        <div class="form__div">
                                            <input required type="password" class="form-control" placeholder=" " name="ccv_code">
                                            <label for="" class="form__label">kod cvv</label>
                                        </div>
                                    </div>
                                    <div class="col-12">
                                        <div class="form__div">
                                            <input type="text" class="form-control" placeholder=" " name="card_number">
                                            <label for="" class="form__label">Nazwa karty</label>
                                        </div>
                                    </div>
                                </div>
                                <div class="col-12">
                                    <button class="btn btn-primary payment" type="submit">
                                        Zapłać
                                    </button>
                                </div>
                            </form>
                            </div>
                        </div>
                    </div>
                </div>
            </div
        </div>
    `
}
