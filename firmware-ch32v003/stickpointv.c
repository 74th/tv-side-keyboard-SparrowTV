#include "ch32v003fun.h"
#include "stickpointv.h"
#include "ch32v003_GPIO_branchless.h"
#include <stdio.h>

#define I2C_SLAVE_ADDRESS 0xA

#define ADC_NUMCHLS 3
#define I2C_BUF_SIZE 8
#define ROW1_PIN GPIOv_from_PORT_PIN(GPIO_port_D, 3)
#define ROW2_PIN GPIOv_from_PORT_PIN(GPIO_port_D, 4)
#define ROW3_PIN GPIOv_from_PORT_PIN(GPIO_port_D, 6)
#define COL1_PIN GPIOv_from_PORT_PIN(GPIO_port_D, 2)
#define COL2_PIN GPIOv_from_PORT_PIN(GPIO_port_C, 7)
#define COL3_PIN GPIOv_from_PORT_PIN(GPIO_port_C, 6)
#define COL4_PIN GPIOv_from_PORT_PIN(GPIO_port_C, 5)
#define COL5_PIN GPIOv_from_PORT_PIN(GPIO_port_C, 3)

volatile uint8_t i2c_buf[I2C_BUF_SIZE];
volatile uint16_t adc_buf[ADC_NUMCHLS];

void I2C1_EV_IRQHandler(void) __attribute__((interrupt));
void I2C1_ER_IRQHandler(void) __attribute__((interrupt));

void init_rcc(void)
{
    RCC->CFGR0 &= ~(0x1F << 11);

    RCC->APB2PCENR |= RCC_APB2Periph_GPIOA | RCC_APB2Periph_GPIOC | RCC_APB2Periph_GPIOD | RCC_APB2Periph_ADC1;
    RCC->APB1PCENR |= RCC_APB1Periph_I2C1;
}

void init_i2c_slave(uint8_t address)
{
    // https://github.com/cnlohr/ch32v003fun/blob/master/examples/i2c_slave/i2c_slave.h

    // PC1 is SDA, 10MHz Output, alt func, open-drain
    GPIOC->CFGLR &= ~(0xf << (4 * 1));
    GPIOC->CFGLR |= (GPIO_Speed_10MHz | GPIO_CNF_OUT_OD_AF) << (4 * 1);

    // PC2 is SCL, 10MHz Output, alt func, open-drain
    GPIOC->CFGLR &= ~(0xf << (4 * 2));
    GPIOC->CFGLR |= (GPIO_Speed_10MHz | GPIO_CNF_OUT_OD_AF) << (4 * 2);

    // Reset I2C1 to init all regs
    RCC->APB1PRSTR |= RCC_APB1Periph_I2C1;
    RCC->APB1PRSTR &= ~RCC_APB1Periph_I2C1;

    I2C1->CTLR1 |= I2C_CTLR1_SWRST;
    I2C1->CTLR1 &= ~I2C_CTLR1_SWRST;

    // Set module clock frequency
    uint32_t prerate = 2000000; // I2C Logic clock rate, must be higher than the bus clock rate
    I2C1->CTLR2 |= (APB_CLOCK / prerate) & I2C_CTLR2_FREQ;

    // Enable interrupts
    I2C1->CTLR2 |= I2C_CTLR2_ITBUFEN;
    I2C1->CTLR2 |= I2C_CTLR2_ITEVTEN; // Event interrupt
    I2C1->CTLR2 |= I2C_CTLR2_ITERREN; // Error interrupt

    NVIC_EnableIRQ(I2C1_EV_IRQn); // Event interrupt
    NVIC_SetPriority(I2C1_EV_IRQn, 2 << 4);
    NVIC_EnableIRQ(I2C1_ER_IRQn); // Error interrupt
    // Set clock configuration
    uint32_t clockrate = 1000000;                                                    // I2C Bus clock rate, must be lower than the logic clock rate
    I2C1->CKCFGR = ((APB_CLOCK / (3 * clockrate)) & I2C_CKCFGR_CCR) | I2C_CKCFGR_FS; // Fast mode 33% duty cycle
    // I2C1->CKCFGR = ((APB_CLOCK/(25*clockrate))&I2C_CKCFGR_CCR) | I2C_CKCFGR_DUTY | I2C_CKCFGR_FS; // Fast mode 36% duty cycle
    // I2C1->CKCFGR = (APB_CLOCK/(2*clockrate))&I2C_CKCFGR_CCR; // Standard mode good to 100kHz

    // Set I2C address
    I2C1->OADDR1 = address << 1;

    // Enable I2C
    I2C1->CTLR1 |= I2C_CTLR1_PE;

    // Acknowledge the first address match event when it happens
    I2C1->CTLR1 |= I2C_CTLR1_ACK;
}

void init_adc(void)
{
    // https://github.com/cnlohr/ch32v003fun/tree/master/examples/adc_dma_opamp

    // ADCCLK = 24 MHz => RCC_ADCPRE = 0: divide by 2
    RCC->CFGR0 &= ~(0x1F << 11);

    // A0 PA2
    GPIOA->CFGLR &= ~(0xf << (4 * 2)); // CNF = 00: Analog, MODE = 00: Input

    // A1 PA1
    GPIOA->CFGLR &= ~(0xf << (4 * 2)); // CNF = 00: Analog, MODE = 00: Input

    // A2 PA4
    GPIOC->CFGLR &= ~(0xf << (4 * 4)); // CNF = 00: Analog, MODE = 00: Input

    // Reset the ADC to init all regs
    RCC->APB2PRSTR |= RCC_APB2Periph_ADC1;
    RCC->APB2PRSTR &= ~RCC_APB2Periph_ADC1;

    // Set up four conversions on chl 0, 1, 2
    ADC1->RSQR1 = (ADC_NUMCHLS - 1) << 20; // four chls in the sequence
    ADC1->RSQR2 = 0;
    ADC1->RSQR3 = (0 << (5 * 0)) | (1 << (5 * 1)) | (2 << (5 * 2));

    // set sampling time for chl 7, 4, 3, 2
    // 0:7 => 3/9/15/30/43/57/73/241 cycles
    ADC1->SAMPTR2 = (7 << (3 * 0)) | (7 << (3 * 1)) | (7 << (3 * 2));

    // turn on ADC
    ADC1->CTLR2 |= ADC_ADON;

    // Reset calibration
    ADC1->CTLR2 |= ADC_RSTCAL;
    while (ADC1->CTLR2 & ADC_RSTCAL)
        ;

    // Calibrate
    ADC1->CTLR2 |= ADC_CAL;
    while (ADC1->CTLR2 & ADC_CAL)
        ;

    // Turn on DMA
    RCC->AHBPCENR |= RCC_AHBPeriph_DMA1;

    // DMA1_Channel1 is for ADC
    DMA1_Channel1->PADDR = (uint32_t)&ADC1->RDATAR;
    DMA1_Channel1->MADDR = (uint32_t)adc_buf;
    DMA1_Channel1->CNTR = ADC_NUMCHLS;
    DMA1_Channel1->CFGR =
        DMA_M2M_Disable |
        DMA_Priority_VeryHigh |
        DMA_MemoryDataSize_HalfWord |
        DMA_PeripheralDataSize_HalfWord |
        DMA_MemoryInc_Enable |
        DMA_Mode_Circular |
        DMA_DIR_PeripheralSRC;

    // Turn on DMA channel 1
    DMA1_Channel1->CFGR |= DMA_CFGR1_EN;

    // enable scanning
    ADC1->CTLR1 |= ADC_SCAN;

    // Enable continuous conversion and DMA
    ADC1->CTLR2 |= ADC_CONT | ADC_DMA | ADC_EXTSEL;

    // start conversion
    ADC1->CTLR2 |= ADC_SWSTART;
}

void init_gpio(void)
{
    GPIO_port_enable(GPIO_port_C);
    GPIO_port_enable(GPIO_port_D);
    GPIO_pinMode(ROW1_PIN, GPIO_pinMode_I_pullDown, GPIO_Speed_10MHz);
    GPIO_pinMode(ROW2_PIN, GPIO_pinMode_I_pullDown, GPIO_Speed_10MHz);
    GPIO_pinMode(ROW3_PIN, GPIO_pinMode_I_pullDown, GPIO_Speed_10MHz);
    GPIO_pinMode(COL1_PIN, GPIO_pinMode_O_pushPull, GPIO_Speed_10MHz);
    GPIO_pinMode(COL2_PIN, GPIO_pinMode_O_pushPull, GPIO_Speed_10MHz);
    GPIO_pinMode(COL3_PIN, GPIO_pinMode_O_pushPull, GPIO_Speed_10MHz);
    GPIO_pinMode(COL4_PIN, GPIO_pinMode_O_pushPull, GPIO_Speed_10MHz);
    GPIO_pinMode(COL5_PIN, GPIO_pinMode_O_pushPull, GPIO_Speed_10MHz);
}

uint8_t i2c_scan_position = 0;

void I2C1_EV_IRQHandler(void)
{
    uint16_t STAR1, STAR2 __attribute__((unused));
    STAR1 = I2C1->STAR1;
    STAR2 = I2C1->STAR2;

#ifdef FUNCONF_USE_UARTPRINTF
    printf("EV STAR1: 0x%04x STAR2: 0x%04x\r\n", STAR1, STAR2);
#endif

    I2C1->CTLR1 |= I2C_CTLR1_ACK;

    if (STAR1 & I2C_STAR1_ADDR) // 0x0002
    {
#ifdef FUNCONF_USE_UARTPRINTF
        printf("ADDR\r\n");
#endif
        // 最初のイベント
        // read でも write でも必ず最初に呼ばれる
        i2c_scan_position = 0;
    }

    if (STAR1 & I2C_STAR1_RXNE) // 0x0040
    {
#ifdef FUNCONF_USE_UARTPRINTF
        printf("RXNE write event: pos:%d\r\n", i2c_scan_position);
#endif
        // 1byte 受信
        I2C1->DATAR;
    }

    if (STAR1 & I2C_STAR1_TXE) // 0x0080
    {
        // 1byte の read イベント（slave -> master）
#ifdef FUNCONF_USE_UARTPRINTF
        printf("TXE write event: pos:%d\r\n", i2c_scan_position);
#endif
        if (i2c_scan_position < I2C_BUF_SIZE)
        {
            // 1byte 送信
            uint8_t data = i2c_buf[i2c_scan_position];
            I2C1->DATAR = data;
            i2c_scan_position++;
        }
        else
        {
            // 1byte 送信
            I2C1->DATAR = 0x00;
        }
    }
}

void I2C1_ER_IRQHandler(void)
{
    uint16_t STAR1 = I2C1->STAR1;

#ifdef FUNCONF_USE_UARTPRINTF
    printf("ER STAR1: 0x%04x\r\n", STAR1);
#endif

    if (STAR1 & I2C_STAR1_BERR)           // 0x0100
    {                                     // Bus error
        I2C1->STAR1 &= ~(I2C_STAR1_BERR); // Clear error
    }

    if (STAR1 & I2C_STAR1_ARLO)           // 0x0200
    {                                     // Arbitration lost error
        I2C1->STAR1 &= ~(I2C_STAR1_ARLO); // Clear error
    }

    if (STAR1 & I2C_STAR1_AF)           // 0x0400
    {                                   // Acknowledge failure
        I2C1->STAR1 &= ~(I2C_STAR1_AF); // Clear error
    }
}

// const int max = 1024;
const int32_t deadzone = 100;
const int32_t high_zone = 7;
const int32_t middle = 200;
const uint32_t loop_ms = 12;
const uint32_t max_ms = 4028;

int32_t last_center_ms = 0;
int32_t last_high_ms = 0;
int8_t in_dash = 0;

void read_analog(int32_t vcc, int32_t a, int32_t *under, int32_t *upper)
{

    int32_t max = vcc;
    int32_t center = vcc / 2;
    if (a < high_zone)
    {
        *under = 5;
    }
    else if (a < middle)
    {
        *under = 3;
    }
    else if (a < center - deadzone)
    {
        *under = 1;
    }
    else
    {
        *under = 0;
    }

    if (max - high_zone < a)
    {
        *upper = 5;
    }
    else if (max - middle < a)
    {
        *upper = 3;
    }
    else if (center + deadzone < a)
    {
        *upper = 1;
    }
    else
    {
        *upper = 0;
    }
}

void read_stick()
{
    int32_t left = 0;
    int32_t right = 0;
    int32_t up = 0;
    int32_t down = 0;

    int32_t raw_vcc = adc_buf[2];
    int32_t raw_x = adc_buf[1];
    int32_t raw_y = adc_buf[0];
    read_analog(raw_vcc, raw_x, &left, &right);
    read_analog(raw_vcc, raw_y, &down, &up);

    if (left == 0 && right == 0)
    {
        last_center_ms = 0;
    }
    else
    {
        if (last_center_ms < max_ms)
        {
            last_center_ms += loop_ms;
        }
    }

    if (left + right + up + down >= 4)
    {
        if (!in_dash && last_center_ms < 300 && 10 < last_high_ms && last_high_ms < 300)
        {
            in_dash = 1;
        }
        if (in_dash)
        {
            left = left * 2;
            right = right * 2;
            up = up * 2;
            down = down * 2;
        }
        last_high_ms = 0;
    }
    else
    {
        in_dash = 0;
        if (last_high_ms < max_ms)
        {
            last_high_ms += loop_ms;
        }
    }

    i2c_buf[0] = (uint8_t)up;
    i2c_buf[1] = (uint8_t)down;
    i2c_buf[2] = (uint8_t)left;
    i2c_buf[3] = (uint8_t)right;
    i2c_buf[4] = (uint8_t)0;

    // printf("raw_x: %d, raw_y: %d, raw_vcc: %d\r\n", raw_x, raw_y, raw_vcc);
}

void read_switch()
{
    uint8_t row1_buf = 0;
    uint8_t row2_buf = 0;
    uint8_t row3_buf = 0;
    for (int col = 0; col < 5; col++)
    {
        switch (col)
        {
        case 0:
            GPIO_digitalWrite_1(COL1_PIN);
            GPIO_digitalWrite_0(COL2_PIN);
            GPIO_digitalWrite_0(COL3_PIN);
            GPIO_digitalWrite_0(COL4_PIN);
            GPIO_digitalWrite_0(COL5_PIN);
            break;
        case 1:
            GPIO_digitalWrite_0(COL1_PIN);
            GPIO_digitalWrite_1(COL2_PIN);
            GPIO_digitalWrite_0(COL3_PIN);
            GPIO_digitalWrite_0(COL4_PIN);
            GPIO_digitalWrite_0(COL5_PIN);
            break;
        case 2:
            GPIO_digitalWrite_0(COL1_PIN);
            GPIO_digitalWrite_0(COL2_PIN);
            GPIO_digitalWrite_1(COL3_PIN);
            GPIO_digitalWrite_0(COL4_PIN);
            GPIO_digitalWrite_0(COL5_PIN);
            break;
        case 3:
            GPIO_digitalWrite_0(COL1_PIN);
            GPIO_digitalWrite_0(COL2_PIN);
            GPIO_digitalWrite_0(COL3_PIN);
            GPIO_digitalWrite_1(COL4_PIN);
            GPIO_digitalWrite_0(COL5_PIN);
            break;
        case 4:
            GPIO_digitalWrite_0(COL1_PIN);
            GPIO_digitalWrite_0(COL2_PIN);
            GPIO_digitalWrite_0(COL3_PIN);
            GPIO_digitalWrite_0(COL4_PIN);
            GPIO_digitalWrite_1(COL5_PIN);
            break;
        }

        Delay_Us(1);

        row1_buf |= GPIO_digitalRead(ROW1_PIN) << col;
        row2_buf |= GPIO_digitalRead(ROW2_PIN) << col;
        row3_buf |= GPIO_digitalRead(ROW3_PIN) << col;
    }
    i2c_buf[5] = row1_buf;
    i2c_buf[6] = row2_buf;
    i2c_buf[7] = row3_buf;

    // printf("row1: %02X, row1: %02X, row2: %02X\r\n", row1_buf, row2_buf, row3_buf);
}

void raw_adc_test()
{
    uint16_t raw_vcc = adc_buf[2];
    uint16_t raw_x = adc_buf[0];
    uint16_t raw_y = adc_buf[1];
    i2c_buf[0] = (uint8_t)(raw_x >> 2);
    i2c_buf[1] = (uint8_t)(raw_y >> 2);
    i2c_buf[2] = (uint8_t)(raw_vcc >> 2);
    i2c_buf[3] = (uint8_t)0;
    i2c_buf[4] = (uint8_t)0;

    // i2c_buf[0] = (uint8_t)((0xff00 & raw_x) >> 8);
    // i2c_buf[1] = (uint8_t)((0x00ff & raw_x));
    // i2c_buf[2] = (uint8_t)((0xff00 & raw_y) >> 8);
    // i2c_buf[3] = (uint8_t)((0x00ff & raw_y));
}

int main()
{
    SystemInit();
    init_rcc();

    printf("using ch32v003fun\r\n");
    printf("initialize\r\n");

    init_i2c_slave(I2C_SLAVE_ADDRESS);
    init_adc();
    init_gpio();

    printf("initialize done\r\n");

    while (1)
    {
        read_stick();
        read_switch();
        Delay_Ms(loop_ms);
        // raw_adc_test();
        // Delay_Ms(500);
    }
}
