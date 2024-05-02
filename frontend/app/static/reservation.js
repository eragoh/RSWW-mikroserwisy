export default {
    name: 'Reservation',
    props: ['tourid'],
    components: {},
    data() {
        return {
            tour: null,
            countdown: 60,
            timer: null,
            formData: {
                adults: 1,
                children3: 0,
                children10: 0,
                children18: 0
            },
            price: 0,
        }
    },
    methods: {
        calculate_price: function(){
            var sum = 0;
            sum += this.formData.adults * this.tour.price;
            sum += this.formData.children3 * 0.5 * this.tour.price;
            sum += this.formData.children10 * 0.7 * this.tour.price;
            sum += this.formData.children18 * 0.8 * this.tour.price;
            this.price = sum.toFixed(2);
        },

        load: async function(){
            const url = '/tours/' + this.tourid + '/get/';
            this.tour = await (await fetch(url)).json();
            
            const url_minute = '/tours/' + this.tourid + '/minute/';
            var clocktimer = await (await fetch(url_minute)).json();
            this.countdown = clocktimer.clock;
            this.timer = setInterval(() => {
                if (this.countdown > 0) {
                    this.countdown--;
                } else {
                    clearInterval(this.timer);
                    window.location.href = '/tours/' + this.tourid;
                }
            }, 1000);
            this.calculate_price();
        },
    },
    watch: {
        formData: {
            handler: function(newValue, oldValue) {
                this.calculate_price();
            },
            deep: true
        }
    },
    mounted() {
        this.load();
    },
    template: /*html*/`
    <div v-if="tour">
        <div class="row">
            <div class="col-lg-4 mb-lg-0 mb-3">
                <div class="card p-3">
                    <div class="countdown">
                        <p>
                            <h3>Pozostały czas do dokonania rezerwacji: 00:{{ countdown > 9 ? countdown : '0' + countdown }}</h3>
                        </p>
                    </div>
                </div>
            </div>
    
            <div class="col-12 mt-4">
                <div class="card p-3">
                    <p class="mb-0 fw-bold h4">Przejdź do płatności</p>
                </div>
            </div>

            <div class="col-12">
                <div class="card p-3">
                    <div class="card-body border p-0">
                        <p>
                            <a class="btn btn-primary p-2 w-100 h-100 d-flex align-items-center justify-content-between"
                                data-bs-toggle="collapse" href="#collapseExample" role="button" aria-expanded="true"
                                aria-controls="collapseExample">
                                <span class="fw-bold">Uczestnicy</span>
                                <span class="">
                                    <span class="fab fa-cc-amex"></span>
                                    <span class="fab fa-cc-mastercard"></span>
                                    <span class="fab fa-cc-discover"></span>
                                </span>
                            </a>
                        </p>
                        <div class="collapse show p-3 pt-0" id="collapseExample">
                            <div class="row">
                                <div class="col-lg-5 mb-lg-0 mb-3">
                                    <p class="h4 mb-0">Podsumowanie</p>
                                </div>
                                <div class="col-lg-7">
                                    <form class="form" method="post">
                                        <div class="form__div">
                                            <label for="adults">Liczba dorosłych</label>
                                            <select class="form-control" id="adults" name="adults" v-model="formData.adults">
                                                <option v-for="index in tour.adults" :key="index">
                                                    {{index}}
                                                </option>
                                            </select>
                                        </div>
                                        <div class="row">
                                            <div class="form__div col-4">
                                                <label for="children3">Liczba dzieci (do 3 lat)</label>
                                                <select class="form-control" id="children3" name="children3" v-model="formData.children3">
                                                    <option v-for="index in tour.children_under_3 + 1" :key="index">
                                                        {{index - 1}}
                                                    </option>
                                                </select>
                                            </div>
                                            <div class="form__div col-4">
                                                <label for="children10">Liczba dzieci (do 10 lat)</label>
                                                <select class="form-control" id="children10" name="children10" v-model="formData.children10">
                                                    <option v-for="index in tour.children_under_10 + 1" :key="index">
                                                        {{index - 1}}
                                                    </option>
                                                </select>
                                            </div>
                                            <div class="form__div col-4">
                                                <label for="children18">Liczba dzieci (do 18 lat)</label>
                                                <select class="form-control" id="children18" name="children18" v-model="formData.children18">
                                                    <option v-for="index in tour.children_under_18 + 1" :key="index">
                                                        {{index - 1}}
                                                    </option>
                                                </select>
                                            </div>
                                        </div>
                                    </form>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div class="col-12">
                <div class="card p-3">
                    <div class="card-body border p-0">
                        <p>
                            <a class="btn btn-primary p-2 w-100 h-100 d-flex align-items-center justify-content-between"
                                data-bs-toggle="collapse" href="#collapseExample2" role="button" aria-expanded="true"
                                aria-controls="collapseExample2">
                                <span class="fw-bold">Karta kredytowa</span>
                                <span class="">
                                    <span class="fab fa-cc-amex"></span>
                                    <span class="fab fa-cc-mastercard"></span>
                                    <span class="fab fa-cc-discover"></span>
                                </span>
                            </a>
                        </p>
                        <div class="collapse show p-3 pt-0" id="collapseExample2">
                            <div class="row">
                                <div class="col-lg-5 mb-lg-0 mb-3">
                                    <p class="h4 mb-0">Podsumowanie</p>
                                    <p class="mb-0"><span class="fw-bold">Produkt: </span><span class="c-green"> {{tour.hotel}}</span></p>
                                    <p class="mb-0"><span class="fw-bold">Miejsce: </span><span class="c-green"> {{ tour.country }}{{ tour.city !== '' ? ', ' + tour.city : '' }}</span></p>
                                    <p class="mb-0 text-truncate">
                                        {{tour.description}}
                                    </p>
                                </div>
                                <div class="col-lg-7">
                                    <form class="form" method="post">
                                           <div class="row">
                                            <div class="col-12">
                                                <div class="form__div">
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
                </div>
            </div>
        </div>
    </div>

    <div v-else>
        <p>😔 Wystąpił błąd ex1024865. Sprawdź ponownie swoje dane. 😔</p>
    </div>
    <br />
    `
}
